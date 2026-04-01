"""
Prepare training dataset with captions for LoRA fine-tuning.

This script creates text caption files for each image in the dataset.
Captions are essential for teaching the model what "Yoto Player style" means.

You can either:
  1. Auto-generate captions using BLIP (requires GPU)
  2. Use a template-based approach (no GPU needed)
  3. Manually edit the generated caption files

Usage:
  # Template-based captions (recommended to start):
  python prepare_dataset.py --image-dir ../dataset/images --method template

  # Auto-caption with BLIP model:
  python prepare_dataset.py --image-dir ../dataset/images --method blip

  # Custom trigger word (used to activate your style during generation):
  python prepare_dataset.py --image-dir ../dataset/images --method template --trigger "yotoicon"
"""

import argparse
import os
from pathlib import Path

from PIL import Image


# Default trigger word - this is what you'll use in prompts to activate the style
DEFAULT_TRIGGER = "yotoicon"

# Template captions that describe the Yoto icon style
STYLE_DESCRIPTION = (
    "a {trigger} style illustration, colorful flat design icon, "
    "simple clean vector art, rounded shapes, soft pastel colors, "
    "children's book illustration style, yoto player card artwork"
)


def create_template_captions(image_dir: str, trigger: str):
    """Create template-based caption files for each image."""
    image_dir = Path(image_dir)
    valid_extensions = {".png", ".jpg", ".jpeg", ".webp"}

    images = [
        f for f in image_dir.iterdir()
        if f.is_file() and f.suffix.lower() in valid_extensions
    ]

    print(f"Found {len(images)} images in {image_dir}")
    print(f"Using trigger word: '{trigger}'")
    print(f"Style description: {STYLE_DESCRIPTION.format(trigger=trigger)}")
    print()

    for img_path in sorted(images):
        caption_path = img_path.with_suffix(".txt")
        caption = STYLE_DESCRIPTION.format(trigger=trigger)

        # Try to infer subject from filename
        name = img_path.stem.lower()
        # Remove prefix like "yoto_0001"
        for prefix in ("yoto_", "icon_", "img_"):
            name = name.replace(prefix, "")
        # Remove numbers
        name = "".join(c for c in name if not c.isdigit()).strip("_- ")

        if name:
            caption = f"{caption}, {name}"

        with open(caption_path, "w") as f:
            f.write(caption)

        print(f"  {img_path.name} -> {caption_path.name}")

    print(f"\nCreated {len(images)} caption files.")
    print("TIP: Edit the .txt files to add specific descriptions for better results!")


def create_blip_captions(image_dir: str, trigger: str):
    """Auto-generate captions using BLIP model, then prepend trigger word."""
    try:
        import torch
        from transformers import BlipForConditionalGeneration, BlipProcessor
    except ImportError:
        print("ERROR: BLIP captioning requires 'transformers' and 'torch'.")
        print("Install with: pip install transformers torch")
        return

    image_dir = Path(image_dir)
    valid_extensions = {".png", ".jpg", ".jpeg", ".webp"}

    images = [
        f for f in image_dir.iterdir()
        if f.is_file() and f.suffix.lower() in valid_extensions
    ]

    print(f"Found {len(images)} images")
    print("Loading BLIP model (this may take a moment)...")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained(
        "Salesforce/blip-image-captioning-base"
    ).to(device)

    print(f"Using device: {device}\n")

    for img_path in sorted(images):
        try:
            img = Image.open(img_path).convert("RGB")
            inputs = processor(img, return_tensors="pt").to(device)

            with torch.no_grad():
                output = model.generate(**inputs, max_new_tokens=50)

            caption = processor.decode(output[0], skip_special_tokens=True)

            # Prepend trigger word and style description
            full_caption = (
                f"a {trigger} style illustration, {caption}, "
                "colorful flat design icon, yoto player card artwork"
            )

            caption_path = img_path.with_suffix(".txt")
            with open(caption_path, "w") as f:
                f.write(full_caption)

            print(f"  {img_path.name}: {full_caption}")

        except Exception as e:
            print(f"  ERROR on {img_path.name}: {e}")

    print(f"\nGenerated {len(images)} captions with BLIP.")


def validate_dataset(image_dir: str):
    """Check that the dataset is ready for training."""
    image_dir = Path(image_dir)
    valid_extensions = {".png", ".jpg", ".jpeg", ".webp"}

    images = [
        f for f in image_dir.iterdir()
        if f.is_file() and f.suffix.lower() in valid_extensions
    ]
    captions = [f for f in image_dir.iterdir() if f.suffix == ".txt"]

    print("Dataset Validation:")
    print(f"  Images:   {len(images)}")
    print(f"  Captions: {len(captions)}")

    # Check that every image has a caption
    missing_captions = []
    for img in images:
        if not img.with_suffix(".txt").exists():
            missing_captions.append(img.name)

    if missing_captions:
        print(f"\n  WARNING: {len(missing_captions)} images missing captions:")
        for name in missing_captions[:10]:
            print(f"    - {name}")
    else:
        print("\n  All images have matching caption files!")

    if len(images) < 10:
        print(f"\n  WARNING: Only {len(images)} images. Recommend at least 15-30 for good results.")
    elif len(images) < 30:
        print(f"\n  OK: {len(images)} images. This should work, but 30+ is ideal.")
    else:
        print(f"\n  GREAT: {len(images)} images is a solid dataset size.")

    return len(missing_captions) == 0


def main():
    parser = argparse.ArgumentParser(
        description="Prepare training dataset with captions for Yoto icon style training"
    )
    parser.add_argument(
        "--image-dir",
        default="../dataset/images",
        help="Directory containing training images",
    )
    parser.add_argument(
        "--method",
        choices=["template", "blip", "validate"],
        default="template",
        help="Captioning method: 'template' (no GPU), 'blip' (auto-caption), 'validate' (check dataset)",
    )
    parser.add_argument(
        "--trigger",
        default=DEFAULT_TRIGGER,
        help=f"Trigger word for the style (default: '{DEFAULT_TRIGGER}')",
    )

    args = parser.parse_args()

    if args.method == "template":
        create_template_captions(args.image_dir, args.trigger)
    elif args.method == "blip":
        create_blip_captions(args.image_dir, args.trigger)
    elif args.method == "validate":
        validate_dataset(args.image_dir)


if __name__ == "__main__":
    main()
