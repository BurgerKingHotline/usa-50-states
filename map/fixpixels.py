from pathlib import Path
from PIL import Image
import csv

script_dir = Path(__file__).resolve().parent

image_path = script_dir / "input.png"
coords_path = script_dir / "pixels.csv"
output_path = script_dir / "output.png"

img = Image.open(image_path).convert("RGBA")
pixels = img.load()
width, height = img.size

with open(coords_path, newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        x = int(row["x"])
        y = int(row["y"])

        source_x = x + 1
        source_y = y

        if 0 <= x < width and 0 <= y < height and 0 <= source_x < width:
            pixels[x, y] = pixels[source_x, source_y]

img.save(output_path)