from PIL import Image
import os

source_image = r"C:\Users\MSI-Owen\.gemini\antigravity-cli\brain\9bd44f6b-ee84-4001-824a-76e30a0abbe1\owen_app_icon_1783576811593.jpg"
base_dir = r"C:\Users\MSI-Owen\Documents\APK Easy Tool v1.60 Portable\1-Decompiled APKs\Clash of SL 8.709.1v\res"

sizes = {
    "drawable-ldpi-v4": 36,
    "drawable-mdpi-v4": 48,
    "drawable-hdpi-v4": 72,
    "drawable-xhdpi-v4": 96,
    "drawable-xxhdpi-v4": 144,
    "drawable-xxxhdpi-v4": 192,
}

img = Image.open(source_image)

for folder, size in sizes.items():
    target_folder = os.path.join(base_dir, folder)
    if os.path.exists(target_folder):
        target_file = os.path.join(target_folder, "ic_launcher.png")
        resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
        resized_img.save(target_file, "PNG")
        print(f"Saved {size}x{size} icon to {target_file}")
