import os
from pathlib import Path
from PIL import Image

IMG_FORMATS = ["png", "webp"]
BACKGROUND_COLORS = {
    "white": (255, 255, 255, 255),
    "black": (0, 0, 0, 255),
}


def convert_images(png_path, sizes, quality=95, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(png_path))[0]

    # Carica l'immagine di input
    img = Image.open(png_path).convert("RGBA")

    for width, height in sizes:
        resized = resize_and_crop_center(img, (width, height))
        for format in IMG_FORMATS:
            path = os.path.join(
                output_dir, f"{base_name}_{resized.size[0]}x{resized.size[1]}.{format}"
            )
            resized.save(path, format=format.upper(), quality=quality)

            for k in BACKGROUND_COLORS:
                color = BACKGROUND_COLORS[k]
                background = Image.new("RGBA", resized.size, color)
                background.paste(resized, (0, 0), resized)
                background_path = os.path.join(
                    output_dir,
                    f"{base_name}_{resized.size[0]}x{resized.size[1]}_{k}.{format}",
                )
                background.save(background_path, format=format.upper(), quality=quality)

    print("✅ Images generated!")

    # Favicon
    generate_favicon(img, base_name, output_dir)
    print("✅ Favicons generated!")

    # Apple touch icons
    generate_apple_touch_icons(img, base_name, output_dir)
    print("✅ Apple touch icons generated!")


def resize_and_crop_center(img, target_size):
    target_width, target_height = target_size
    original_width, original_height = img.size

    assert target_height or target_width, "Target size must have at least one dimension"

    if target_width is None:
        target_width = int(original_width * (target_height / original_height))
    if target_height is None:
        target_height = int(original_height * (target_width / original_width))
    if target_width == original_width and target_height == original_height:
        return img

    scale = min(target_width / original_width, target_height / original_height)
    new_size = (int(original_width * scale), int(original_height * scale))
    resized_img = img.resize(new_size, Image.LANCZOS)
    left = (resized_img.width - target_width) // 2
    top = (resized_img.height - target_height) // 2
    _img = resized_img.crop((left, top, left + target_width, top + target_height))
    if target_size[0] is None or target_size[1] is None:
        _img = add_padding_around_image(_img, target_size)
    return _img


def add_padding_around_image(img, target_size):
    target_width, target_height = target_size
    original_width, original_height = img.size

    if target_width is None:
        target_width = int(original_width * (target_height / original_height))
    if target_height is None:
        target_height = int(original_height * (target_width / original_width))

    new_img = Image.new("RGBA", (target_width, target_height), (255, 255, 255, 0))
    left = (target_width - original_width) // 2
    top = (target_height - original_height) // 2
    new_img.paste(img, (left, top))
    return new_img


def generate_favicon(source_img, base_name, output_dir):
    favicon_sizes = [16, 32, 48]
    icons = [resize_and_crop_center(source_img, (s, None)) for s in favicon_sizes]
    for icon in icons:
        ico_path = os.path.join(
            output_dir, f"{base_name}_favicon_{icon.size[0]}x{icon.size[1]}.ico"
        )
        icon = icon.save(ico_path, format="ICO", sizes=[(s, s) for s in favicon_sizes])


def generate_apple_touch_icons(source_img, base_name, output_dir):
    for size in [180, 152, 120, 76]:
        resized = resize_and_crop_center(source_img, (size, size))
        for format in IMG_FORMATS:
            path = os.path.join(
                output_dir,
                f"{base_name}_apple_{resized.size[0]}x{resized.size[1]}.{format}",
            )
            resized.save(path, format=format.upper())


if __name__ == "__main__":

    config = {
        "logo.png": [
            (16, 16),
            (32, 32),
            (140, 140),
            (400, 400),
            (192, 192),
            (512, 512),
            (None, 630),
            (None, 200),
            (1200, None),
            (800, 200),
            (1200, 630),
        ],
        "logoG.png": [
            (16, None),
            (32, None),
            (140, None),
            (400, None),
            (192, None),
            (512, None),
        ],
        "logo-big.png": [
            (480, None),
            (800, None),
            (None, 630),
            (None, 200),
            (1200, None),
        ],
        "notfound.png": [(200, 200), (400, 400)],
    }

    dir = Path(__file__).resolve(strict=True).parent
    generated_dir = str(dir / "generated")

    # create the generated folder
    os.makedirs(generated_dir, exist_ok=True)
    # generate the icons
    for png, sizes in config.items():
        png_path = os.path.join(dir, png)
        convert_images(png_path, sizes, output_dir=generated_dir)
