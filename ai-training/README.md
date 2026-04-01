# Yoto Player Icon - AI Image Generator

Train an AI model to generate Yoto Player-style icon images using LoRA fine-tuning on Stable Diffusion XL.

## Requirements

- Python 3.10+
- NVIDIA GPU with 12GB+ VRAM (16GB recommended)
- CUDA toolkit installed
- 15-30+ training images of Yoto Player icons

## Quick Start

### 1. Install Dependencies

```bash
cd ai-training
pip install -r requirements.txt
```

### 2. Collect Training Images

Download animal icons from [yotoicons.com](https://yotoicons.com/icons?category=&tag=animals) manually, then use the download script to resize them:

```bash
# From a folder of manually saved images:
python scripts/download_images.py --source-dir /path/to/saved/icons --output dataset/images

# Or from a file with image URLs (one per line):
python scripts/download_images.py --url-list urls.txt --output dataset/images
```

### 3. Prepare Captions

Each image needs a text caption describing it. The script creates these automatically:

```bash
# Quick template-based captions:
python scripts/prepare_dataset.py --image-dir dataset/images --method template

# Or auto-caption with BLIP (requires GPU):
python scripts/prepare_dataset.py --image-dir dataset/images --method blip

# Validate your dataset is ready:
python scripts/prepare_dataset.py --image-dir dataset/images --method validate
```

**Tip:** Edit the `.txt` caption files to add specific descriptions for better results.

### 4. Train the Model

```bash
python scripts/train_lora.py \
  --dataset-dir dataset/images \
  --output-dir output \
  --epochs 10 \
  --learning-rate 1e-4
```

Training takes ~30-60 minutes on a modern GPU with 20-30 images.

### 5. Generate New Images

```bash
# Generate a single image:
python scripts/generate.py \
  --lora-path output/yoto-icon-lora \
  --prompt "a yotoicon style illustration of a friendly cat"

# Generate example animal icons:
python scripts/generate.py --lora-path output/yoto-icon-lora --examples

# Generate multiple variations:
python scripts/generate.py \
  --lora-path output/yoto-icon-lora \
  --prompt "a yotoicon style illustration of a happy dog" \
  --num-images 4
```

## Project Structure

```
ai-training/
├── README.md
├── requirements.txt
├── dataset/
│   └── images/          # Training images + caption .txt files
├── output/              # Trained model checkpoints
│   ├── checkpoint-*/    # Intermediate checkpoints
│   ├── yoto-icon-lora/  # Final trained LoRA model
│   └── generated/       # Generated images
└── scripts/
    ├── download_images.py   # Download & resize images
    ├── prepare_dataset.py   # Create caption files
    ├── train_lora.py        # Train the LoRA model
    └── generate.py          # Generate new images
```

## Tips for Best Results

- **More images = better results.** Aim for 20-30+ images minimum.
- **Good captions matter.** Edit the auto-generated `.txt` files to be specific and descriptive.
- **Use the trigger word.** Include `yotoicon` in your generation prompts to activate the trained style.
- **Experiment with settings.** Try different guidance scales (5-10) and step counts (20-40).
- **Check intermediate checkpoints.** Sometimes an earlier epoch produces better results than the final one.

## Licensing Note

Before training on images from yotoicons.com or any other source, check their terms of service and licensing. Ensure you have the right to use the images for AI model training.
