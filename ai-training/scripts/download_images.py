"""
Download Yoto Player icon images for training dataset.

Since yotoicons.com blocks automated scraping, this script provides
two approaches:
  1. Download from a local folder of manually saved images
  2. Download from a list of image URLs you provide in a text file

Usage:
  # From a URL list file (one URL per line):
  python download_images.py --url-list urls.txt --output ../dataset/images

  # From a local folder (copies + resizes):
  python download_images.py --source-dir /path/to/saved/icons --output ../dataset/images

  # Resize dimensions (default 512x512 for SDXL training):
  python download_images.py --source-dir ./raw --output ../dataset/images --size 512
"""

import argparse
import os
import sys
from pathlib import Path

import requests
from PIL import Image


def download_from_urls(url_file: str, output_dir: str, size: int):
    """Download images from a text file containing one URL per line."""
    os.makedirs(output_dir, exist_ok=True)

    with open(url_file, "r") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    print(f"Found {len(urls)} URLs to download")

    for i, url in enumerate(urls):
        try:
            print(f"  [{i+1}/{len(urls)}] Downloading: {url}")
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()

            # Determine file extension from content type or URL
            ext = Path(url).suffix.lower()
            if ext not in (".png", ".jpg", ".jpeg", ".webp", ".svg"):
                content_type = response.headers.get("content-type", "")
                if "png" in content_type:
                    ext = ".png"
                elif "jpeg" in content_type or "jpg" in content_type:
                    ext = ".jpg"
                elif "webp" in content_type:
                    ext = ".webp"
                else:
                    ext = ".png"

            filename = f"yoto_{i:04d}{ext}"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "wb") as img_file:
                for chunk in response.iter_content(chunk_size=8192):
                    img_file.write(chunk)

            # Resize if it's a raster image
            if ext != ".svg":
                resize_image(filepath, size)

            print(f"    Saved: {filename}")

        except Exception as e:
            print(f"    ERROR: {e}")

    print(f"\nDone! Downloaded images to: {output_dir}")


def copy_from_directory(source_dir: str, output_dir: str, size: int):
    """Copy and resize images from a local directory."""
    os.makedirs(output_dir, exist_ok=True)

    valid_extensions = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}
    source_path = Path(source_dir)
    images = [
        f for f in source_path.iterdir()
        if f.is_file() and f.suffix.lower() in valid_extensions
    ]

    print(f"Found {len(images)} images in {source_dir}")

    for i, img_path in enumerate(sorted(images)):
        try:
            filename = f"yoto_{i:04d}{img_path.suffix.lower()}"
            output_path = os.path.join(output_dir, filename)

            img = Image.open(img_path).convert("RGB")
            img = img.resize((size, size), Image.LANCZOS)
            img.save(output_path, quality=95)

            print(f"  [{i+1}/{len(images)}] {img_path.name} -> {filename}")

        except Exception as e:
            print(f"  ERROR processing {img_path.name}: {e}")

    print(f"\nDone! Processed {len(images)} images to: {output_dir}")


def resize_image(filepath: str, size: int):
    """Resize an image to the target square dimensions."""
    try:
        img = Image.open(filepath).convert("RGB")
        img = img.resize((size, size), Image.LANCZOS)
        # Save as PNG for consistency
        new_path = Path(filepath).with_suffix(".png")
        img.save(str(new_path), quality=95)
        if str(new_path) != filepath:
            os.remove(filepath)
    except Exception as e:
        print(f"    Warning: Could not resize {filepath}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Download and prepare Yoto Player icon images for AI training"
    )
    parser.add_argument(
        "--url-list",
        help="Path to a text file with one image URL per line",
    )
    parser.add_argument(
        "--source-dir",
        help="Path to a local directory containing downloaded images",
    )
    parser.add_argument(
        "--output",
        default="../dataset/images",
        help="Output directory for processed images (default: ../dataset/images)",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=512,
        help="Target image size in pixels (images resized to size x size, default: 512)",
    )

    args = parser.parse_args()

    if not args.url_list and not args.source_dir:
        print("Error: You must provide either --url-list or --source-dir")
        print("\nExamples:")
        print("  python download_images.py --url-list urls.txt --output ../dataset/images")
        print("  python download_images.py --source-dir ./raw_icons --output ../dataset/images")
        sys.exit(1)

    if args.url_list:
        download_from_urls(args.url_list, args.output, args.size)
    elif args.source_dir:
        copy_from_directory(args.source_dir, args.output, args.size)


if __name__ == "__main__":
    main()
