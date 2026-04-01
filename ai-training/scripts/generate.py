"""
Generate new Yoto Player-style icon images using your trained LoRA model.

Usage:
  # Generate a single image:
  python generate.py --lora-path ../output/yoto-icon-lora --prompt "a yotoicon style illustration of a friendly cat"

  # Generate multiple images:
  python generate.py \
    --lora-path ../output/yoto-icon-lora \
    --prompt "a yotoicon style illustration of a happy dog" \
    --num-images 4

  # Batch generate from a prompt file (one prompt per line):
  python generate.py \
    --lora-path ../output/yoto-icon-lora \
    --prompt-file prompts.txt

  # Adjust generation settings:
  python generate.py \
    --lora-path ../output/yoto-icon-lora \
    --prompt "a yotoicon style illustration of a penguin" \
    --steps 30 \
    --guidance-scale 7.5 \
    --seed 42
"""

import argparse
import os
from datetime import datetime

import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image


# Default negative prompt to improve quality
DEFAULT_NEGATIVE = (
    "blurry, low quality, distorted, deformed, ugly, bad anatomy, "
    "watermark, text, signature, photo, realistic, 3d render"
)

# Example prompts for Yoto Player-style animal icons
EXAMPLE_PROMPTS = [
    "a yotoicon style illustration of a friendly orange cat sitting",
    "a yotoicon style illustration of a happy golden retriever dog",
    "a yotoicon style illustration of a cute baby elephant",
    "a yotoicon style illustration of a colorful parrot on a branch",
    "a yotoicon style illustration of a playful dolphin jumping",
    "a yotoicon style illustration of a fluffy white rabbit",
    "a yotoicon style illustration of a wise owl at night",
    "a yotoicon style illustration of a smiling red fox",
    "a yotoicon style illustration of a gentle panda eating bamboo",
    "a yotoicon style illustration of a majestic lion with a mane",
]


def load_pipeline(base_model: str, lora_path: str, device: str):
    """Load the SDXL pipeline with the trained LoRA weights."""
    print(f"Loading base model: {base_model}")
    pipeline = StableDiffusionXLPipeline.from_pretrained(
        base_model,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        use_safetensors=True,
    )

    # Use a faster scheduler
    pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
        pipeline.scheduler.config
    )

    # Load LoRA weights
    if lora_path and os.path.exists(lora_path):
        print(f"Loading LoRA weights: {lora_path}")
        pipeline.load_lora_weights(lora_path)
    else:
        print("WARNING: No LoRA weights loaded. Using base model only.")

    pipeline.to(device)

    # Enable memory optimizations
    if device == "cuda":
        pipeline.enable_attention_slicing()
        try:
            pipeline.enable_xformers_memory_efficient_attention()
            print("Using xformers memory-efficient attention")
        except Exception:
            print("xformers not available, using default attention")

    return pipeline


def generate_images(pipeline, prompt: str, negative_prompt: str,
                    num_images: int, steps: int, guidance_scale: float,
                    seed: int, resolution: int, output_dir: str):
    """Generate images from a prompt."""
    os.makedirs(output_dir, exist_ok=True)

    generator = None
    if seed >= 0:
        generator = torch.Generator(device=pipeline.device).manual_seed(seed)

    print(f"\nGenerating {num_images} image(s)...")
    print(f"  Prompt: {prompt}")
    print(f"  Steps: {steps} | Guidance: {guidance_scale} | Seed: {seed}")

    images = []
    for i in range(num_images):
        current_seed = seed + i if seed >= 0 else -1
        if current_seed >= 0:
            generator = torch.Generator(device=pipeline.device).manual_seed(current_seed)

        result = pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=steps,
            guidance_scale=guidance_scale,
            generator=generator,
            width=resolution,
            height=resolution,
        )

        image = result.images[0]

        # Save with timestamp and seed
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"yoto_{timestamp}_s{current_seed}_{i}.png"
        filepath = os.path.join(output_dir, filename)
        image.save(filepath)
        images.append(filepath)

        print(f"  Saved: {filepath}")

    return images


def main():
    parser = argparse.ArgumentParser(
        description="Generate Yoto Player-style icon images"
    )
    parser.add_argument(
        "--lora-path",
        default="../output/yoto-icon-lora",
        help="Path to trained LoRA weights",
    )
    parser.add_argument(
        "--base-model",
        default="stabilityai/stable-diffusion-xl-base-1.0",
        help="Base model name",
    )
    parser.add_argument(
        "--prompt",
        help="Text prompt for image generation",
    )
    parser.add_argument(
        "--prompt-file",
        help="File with one prompt per line (generates one image per prompt)",
    )
    parser.add_argument(
        "--negative-prompt",
        default=DEFAULT_NEGATIVE,
        help="Negative prompt to avoid unwanted features",
    )
    parser.add_argument("--num-images", type=int, default=1)
    parser.add_argument("--steps", type=int, default=25)
    parser.add_argument("--guidance-scale", type=float, default=7.5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--resolution", type=int, default=512)
    parser.add_argument("--output-dir", default="../output/generated")
    parser.add_argument(
        "--examples", action="store_true",
        help="Generate images using built-in example prompts",
    )

    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        print("WARNING: Running on CPU. Generation will be very slow.")
        print("A CUDA-capable GPU is strongly recommended.\n")

    pipeline = load_pipeline(args.base_model, args.lora_path, device)

    if args.examples:
        print("\nGenerating example Yoto-style animal icons...\n")
        for i, prompt in enumerate(EXAMPLE_PROMPTS):
            generate_images(
                pipeline, prompt, args.negative_prompt,
                num_images=1, steps=args.steps,
                guidance_scale=args.guidance_scale,
                seed=args.seed + i, resolution=args.resolution,
                output_dir=args.output_dir,
            )
    elif args.prompt_file:
        with open(args.prompt_file, "r") as f:
            prompts = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        print(f"\nGenerating images for {len(prompts)} prompts...\n")
        for i, prompt in enumerate(prompts):
            generate_images(
                pipeline, prompt, args.negative_prompt,
                num_images=1, steps=args.steps,
                guidance_scale=args.guidance_scale,
                seed=args.seed + i, resolution=args.resolution,
                output_dir=args.output_dir,
            )
    elif args.prompt:
        generate_images(
            pipeline, args.prompt, args.negative_prompt,
            num_images=args.num_images, steps=args.steps,
            guidance_scale=args.guidance_scale,
            seed=args.seed, resolution=args.resolution,
            output_dir=args.output_dir,
        )
    else:
        print("No prompt provided. Use --prompt, --prompt-file, or --examples")
        print("\nExample:")
        print('  python generate.py --lora-path ../output/yoto-icon-lora \\')
        print('    --prompt "a yotoicon style illustration of a friendly cat"')


if __name__ == "__main__":
    main()
