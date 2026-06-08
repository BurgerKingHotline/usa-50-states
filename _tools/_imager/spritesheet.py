#!/usr/bin/env python3
"""
SpriteSheet Maker - Merge images from a folder into a single spritesheet.
Uses math and logic to compute optimal grid layout (square-ish by default).
"""

import os
import math
import argparse
from PIL import Image


def create_spritesheet(input_dir, output_file, columns=None, padding=0, bg_color=None):
    """
    Create a spritesheet from all images in input_dir.

    Args:
        input_dir: Folder containing images.
        output_file: Path to save the spritesheet (PNG recommended).
        columns: Number of columns in the grid. If None, auto-calc to be square-ish.
        padding: Pixels between cells and around the sheet.
        bg_color: Background color as (R,G,B) tuple or None for transparent.
    """
    # Get all image files (common formats)
    exts = (".dds", ".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff")
    image_paths = [f for f in os.listdir(input_dir) if f.lower().endswith(exts)]
    if not image_paths:
        print("No images found in the folder.")
        return

    image_paths.sort()  # deterministic order
    images = []
    max_width = 0
    max_height = 0

    # Load images and find max dimensions
    for path in image_paths:
        img = Image.open(os.path.join(input_dir, path)).convert("RGBA")
        images.append(img)
        max_width = max(max_width, img.width)
        max_height = max(max_height, img.height)

    num_images = len(images)
    # Auto-calculate columns if not provided
    if columns is None:
        columns = math.ceil(math.sqrt(num_images))
    rows = math.ceil(num_images / columns)

    # Cell dimensions (uniform, based on max image size + padding)
    cell_w = max_width + padding
    cell_h = max_height + padding

    # Spritesheet dimensions
    sheet_w = columns * cell_w + padding  # outer padding on right
    sheet_h = rows * cell_h + padding  # outer padding on bottom

    # Create background
    if bg_color is None:
        # transparent background
        spritesheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    else:
        spritesheet = Image.new("RGB", (sheet_w, sheet_h), bg_color)

    # Paste each image into its cell
    for idx, img in enumerate(images):
        row = idx // columns
        col = idx % columns
        # Position with padding
        x = col * cell_w + padding
        y = row * cell_h + padding
        # Center smaller images inside the cell (optional)
        offset_x = (max_width - img.width) // 2
        offset_y = (max_height - img.height) // 2
        spritesheet.paste(img, (x + offset_x, y + offset_y), img)

    spritesheet.save(output_file, format="PNG")
    print(f"Spritesheet saved: {output_file}")
    print(
        f"Grid size: {columns} x {rows}  |  Cell size: {max_width}x{max_height}  |  Total images: {num_images}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Merge images in a folder into a spritesheet."
    )
    parser.add_argument("input_dir", help="Folder containing images")
    parser.add_argument(
        "-o", "--output", default="spritesheet.png", help="Output image file (PNG)"
    )
    parser.add_argument(
        "-c", "--columns", type=int, help="Number of columns (auto if not set)"
    )
    parser.add_argument(
        "-p", "--padding", type=int, default=0, help="Padding between cells (pixels)"
    )
    parser.add_argument(
        "--bg",
        nargs=3,
        type=int,
        metavar=("R", "G", "B"),
        help="Background color (e.g. --bg 255 0 0)",
    )

    args = parser.parse_args()
    bg = tuple(args.bg) if args.bg else None
    create_spritesheet(args.input_dir, args.output, args.columns, args.padding, bg)
