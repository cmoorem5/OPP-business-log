# scripts/generate_favicon.py
from PIL import Image
import os

# 1) Load & trim your existing PNG
src_path = os.path.join("assets", "logo-180.png")
img = Image.open(src_path).convert("RGBA")
bbox = img.getbbox()
cropped = img.crop(bbox)

# 2) Scale up to a clean square canvas
square = cropped.resize((256, 256), Image.LANCZOS)
square_path = os.path.join("assets", "logo-256.png")
square.save(square_path, format="PNG")
print(f"Saved trimmed square PNG to {square_path}")

# 3) Generate the multi‐size favicon.ico
ico_path = os.path.join("assets", "favicon.ico")
square.save(
    ico_path,
    format="ICO",
    sizes=[(16,16), (32,32), (64,64), (128,128), (256,256)]
)
print(f"Saved multi‐size favicon to {ico_path}")
