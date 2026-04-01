"""
Train a LoRA (Low-Rank Adaptation) model on Yoto Player icon images.

This fine-tunes Stable Diffusion XL using LoRA so it can generate new images
in the Yoto Player icon style. LoRA is efficient - it only trains a small
number of parameters, so it's faster and uses less memory than full fine-tuning.

Requirements:
  - GPU with at least 12GB VRAM (16GB+ recommended)
  - ~15-30 training images with captions
  - Python packages: diffusers, transformers, accelerate, peft, torch

Usage:
  # Basic training (uses defaults optimized for icon-style images):
  python train_lora.py --dataset-dir ../dataset/images --output-dir ../output

  # Custom training parameters:
  python train_lora.py \
    --dataset-dir ../dataset/images \
    --output-dir ../output \
    --epochs 15 \
    --batch-size 1 \
    --learning-rate 1e-4 \
    --resolution 512

  # Resume from a checkpoint:
  python train_lora.py \
    --dataset-dir ../dataset/images \
    --output-dir ../output \
    --resume-from ../output/checkpoint-500
"""

import argparse
import os
from pathlib import Path

import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from torchvision import transforms


class YotoIconDataset(Dataset):
    """Dataset of Yoto-style icon images with text captions."""

    def __init__(self, image_dir: str, resolution: int = 512):
        self.image_dir = Path(image_dir)
        self.resolution = resolution

        valid_extensions = {".png", ".jpg", ".jpeg", ".webp"}
        self.image_paths = sorted([
            f for f in self.image_dir.iterdir()
            if f.is_file() and f.suffix.lower() in valid_extensions
        ])

        # Filter to only images that have caption files
        self.image_paths = [
            p for p in self.image_paths
            if p.with_suffix(".txt").exists()
        ]

        if len(self.image_paths) == 0:
            raise ValueError(
                f"No images with captions found in {image_dir}. "
                "Run prepare_dataset.py first to create captions."
            )

        self.transform = transforms.Compose([
            transforms.Resize((resolution, resolution), interpolation=transforms.InterpolationMode.LANCZOS),
            transforms.RandomHorizontalFlip(p=0.0),  # Don't flip icons
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5]),  # Normalize to [-1, 1]
        ])

        print(f"Loaded {len(self.image_paths)} image-caption pairs")

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        caption_path = img_path.with_suffix(".txt")

        image = Image.open(img_path).convert("RGB")
        image = self.transform(image)

        with open(caption_path, "r") as f:
            caption = f.read().strip()

        return {"image": image, "caption": caption}


def train(args):
    """Main training loop using diffusers LoRA training."""
    try:
        from diffusers import (
            AutoencoderKL,
            DDPMScheduler,
            StableDiffusionXLPipeline,
            UNet2DConditionModel,
        )
        from diffusers.optimization import get_scheduler
        from transformers import CLIPTextModel, CLIPTokenizer
        from peft import LoraConfig, get_peft_model
        from accelerate import Accelerator
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("\nInstall all requirements with:")
        print("  pip install -r ../requirements.txt")
        return

    print("=" * 60)
    print("Yoto Player Icon - LoRA Training")
    print("=" * 60)
    print(f"  Dataset:       {args.dataset_dir}")
    print(f"  Output:        {args.output_dir}")
    print(f"  Base model:    {args.base_model}")
    print(f"  Resolution:    {args.resolution}x{args.resolution}")
    print(f"  Epochs:        {args.epochs}")
    print(f"  Batch size:    {args.batch_size}")
    print(f"  Learning rate: {args.learning_rate}")
    print(f"  LoRA rank:     {args.lora_rank}")
    print("=" * 60)

    os.makedirs(args.output_dir, exist_ok=True)

    # Initialize accelerator for mixed precision training
    accelerator = Accelerator(
        mixed_precision="fp16" if torch.cuda.is_available() else "no",
        gradient_accumulation_steps=args.gradient_accumulation,
    )

    # Load the base model components
    print("\nLoading base model (this may take a few minutes on first run)...")
    pipeline = StableDiffusionXLPipeline.from_pretrained(
        args.base_model,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        use_safetensors=True,
    )

    unet = pipeline.unet
    vae = pipeline.vae
    text_encoder = pipeline.text_encoder
    text_encoder_2 = pipeline.text_encoder_2
    tokenizer = pipeline.tokenizer
    tokenizer_2 = pipeline.tokenizer_2
    noise_scheduler = DDPMScheduler.from_pretrained(args.base_model, subfolder="scheduler")

    # Freeze all parameters except LoRA
    vae.requires_grad_(False)
    text_encoder.requires_grad_(False)
    text_encoder_2.requires_grad_(False)
    unet.requires_grad_(False)

    # Add LoRA layers to UNet
    print("Adding LoRA layers...")
    lora_config = LoraConfig(
        r=args.lora_rank,
        lora_alpha=args.lora_rank,
        init_lora_weights="gaussian",
        target_modules=[
            "to_k", "to_q", "to_v", "to_out.0",
            "proj_in", "proj_out",
            "ff.net.0.proj", "ff.net.2",
        ],
    )
    unet = get_peft_model(unet, lora_config)
    unet.print_trainable_parameters()

    # Set up dataset and dataloader
    dataset = YotoIconDataset(args.dataset_dir, args.resolution)
    dataloader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=0,
    )

    # Optimizer
    optimizer = torch.optim.AdamW(
        unet.parameters(),
        lr=args.learning_rate,
        weight_decay=1e-2,
    )

    # Learning rate scheduler
    lr_scheduler = get_scheduler(
        "cosine",
        optimizer=optimizer,
        num_warmup_steps=int(0.1 * args.epochs * len(dataloader)),
        num_training_steps=args.epochs * len(dataloader),
    )

    # Prepare with accelerator
    unet, optimizer, dataloader, lr_scheduler = accelerator.prepare(
        unet, optimizer, dataloader, lr_scheduler
    )

    vae.to(accelerator.device)
    text_encoder.to(accelerator.device)
    text_encoder_2.to(accelerator.device)

    # Training loop
    print("\nStarting training...\n")
    global_step = 0

    for epoch in range(args.epochs):
        unet.train()
        epoch_loss = 0.0

        for step, batch in enumerate(dataloader):
            with accelerator.accumulate(unet):
                # Encode images to latent space
                latents = vae.encode(
                    batch["image"].to(dtype=vae.dtype)
                ).latent_dist.sample()
                latents = latents * vae.config.scaling_factor

                # Sample noise
                noise = torch.randn_like(latents)
                timesteps = torch.randint(
                    0, noise_scheduler.config.num_train_timesteps,
                    (latents.shape[0],), device=latents.device
                ).long()

                # Add noise to latents
                noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)

                # Encode text
                captions = batch["caption"]
                text_input_1 = tokenizer(
                    captions, padding="max_length",
                    max_length=tokenizer.model_max_length,
                    truncation=True, return_tensors="pt"
                ).to(accelerator.device)
                text_input_2 = tokenizer_2(
                    captions, padding="max_length",
                    max_length=tokenizer_2.model_max_length,
                    truncation=True, return_tensors="pt"
                ).to(accelerator.device)

                encoder_hidden_states_1 = text_encoder(text_input_1.input_ids)[0]
                encoder_hidden_states_2 = text_encoder_2(text_input_2.input_ids)[0]
                encoder_hidden_states = torch.cat(
                    [encoder_hidden_states_1, encoder_hidden_states_2], dim=-1
                )

                # Predict noise
                model_pred = unet(
                    noisy_latents, timesteps, encoder_hidden_states
                ).sample

                # Compute loss
                loss = torch.nn.functional.mse_loss(
                    model_pred.float(), noise.float(), reduction="mean"
                )

                accelerator.backward(loss)
                optimizer.step()
                lr_scheduler.step()
                optimizer.zero_grad()

                epoch_loss += loss.detach().item()
                global_step += 1

            # Log progress
            if global_step % 10 == 0:
                avg_loss = epoch_loss / (step + 1)
                print(
                    f"  Epoch {epoch+1}/{args.epochs} | "
                    f"Step {step+1}/{len(dataloader)} | "
                    f"Loss: {avg_loss:.4f} | "
                    f"LR: {lr_scheduler.get_last_lr()[0]:.2e}"
                )

        # Save checkpoint each epoch
        checkpoint_dir = os.path.join(args.output_dir, f"checkpoint-epoch-{epoch+1}")
        accelerator.unwrap_model(unet).save_pretrained(checkpoint_dir)
        print(f"\n  Checkpoint saved: {checkpoint_dir}\n")

    # Save final model
    final_dir = os.path.join(args.output_dir, "yoto-icon-lora")
    accelerator.unwrap_model(unet).save_pretrained(final_dir)
    print(f"\nTraining complete! Final LoRA model saved to: {final_dir}")
    print(f"\nTo generate images, run:")
    print(f"  python generate.py --lora-path {final_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Train LoRA model on Yoto Player icon images"
    )
    parser.add_argument(
        "--dataset-dir", default="../dataset/images",
        help="Directory with training images and captions",
    )
    parser.add_argument(
        "--output-dir", default="../output",
        help="Directory to save model checkpoints",
    )
    parser.add_argument(
        "--base-model",
        default="stabilityai/stable-diffusion-xl-base-1.0",
        help="Base model to fine-tune",
    )
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--lora-rank", type=int, default=16)
    parser.add_argument("--resolution", type=int, default=512)
    parser.add_argument("--gradient-accumulation", type=int, default=4)
    parser.add_argument("--resume-from", default=None, help="Path to checkpoint to resume from")

    args = parser.parse_args()
    train(args)


if __name__ == "__main__":
    main()
