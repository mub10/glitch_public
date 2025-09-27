from pathlib import Path
import qrcode
from PIL import Image
import qrcode.image.svg

FORMATS = ["webp", "svg", "png"]
BACKGROUNDS = [
    "white",
    None,
]


def gen_qr(output_file, target_url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(target_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    type(img)
    for format in FORMATS:
        try:
            img.save(f"{output_file}_qr.{format}", format=format.upper())
        except KeyError:
            continue
    print("✅ QR code generated!")


def gen_qr_with_logo(output_file, target_url, logo_path):
    logo = Image.open(logo_path)
    basewidth = 300
    # adjust image size
    wpercent = basewidth / float(logo.size[0])
    hsize = int((float(logo.size[1]) * float(wpercent)))
    logo = logo.resize((basewidth, hsize))
    QRcode = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
    )

    QRcode.add_data(target_url)
    QRcode.make()

    for bg in BACKGROUNDS:
        if bg is not None:
            QRimg = QRcode.make_image(fill_color="black", back_color=bg).convert("RGB")
        else:
            QRimg = QRcode.make_image(fill_color="black", back_color="white").convert(
                "RGBA"
            )
            # Step 4: Make white pixels fully transparent
            pixels = QRimg.getdata()
            new_pixels = []
            for pixel in pixels:
                if pixel[:3] == (255, 255, 255):  # if white
                    new_pixels.append((255, 255, 255, 0))  # transparent
                else:
                    new_pixels.append(pixel)
            QRimg.putdata(new_pixels)

        # set size of QR code
        pos = ((QRimg.size[0] - logo.size[0]) // 2, (QRimg.size[1] - logo.size[1]) // 2)
        QRimg.paste(logo, pos)

        # save the QR code generated
        for format in FORMATS:
            try:
                QRimg.save(
                    f"{output_file}_qrlogo_bg_{str(bg)}.{format}", format=format.upper()
                )
            except KeyError:
                continue

        # svg
        if "svg" in FORMATS:
            qr = qrcode.QRCode(image_factory=qrcode.image.svg.SvgImage, box_size=20)
            qr.add_data(target_url)
            qr.make()
            img = qr.make_image()

            img.save(f"{output_file}_qrlogo_bg_{str(bg)}.svg")
            print("✅ QR code with logo generated!")


if __name__ == "__main__":
    base_url = "https://www.glitch-vra.com"

    for target, target_url in {
        "home": f"{base_url}",
        "events": f"{base_url}/events",
        "book": f"{base_url}/book",
    }.items():

        utms = {
            f"vetrina_to_{target}": {
                "href": f"{target_url}",
                "utm_source": "g",
                "utm_medium": "qr",
                "utm_campaign": "v",
            },
            f"biglietto_da_visita_to_{target}": {
                "href": f"{target_url}",
                "utm_source": "g",
                "utm_medium": "qr",
                "utm_campaign": "b",
            },
            f"locandina_to_{target}": {
                "href": f"{target_url}",
                "utm_source": "g",
                "utm_medium": "qr",
                "utm_campaign": "l",
            },
            f"locandina_jungleparty2025_to_{target}": {
                "href": f"{target_url}",
                "utm_source": "g",
                "utm_medium": "qr",
                "utm_campaign": "ljp25",
            },
        }

        dir = Path(__file__).resolve(strict=True).parent
        logo_path = str(dir.parent / "images" / "logo.png")

        for utm in utms:
            utm_params = "&".join(
                [f"{k}={v}" for k, v in utms[utm].items() if k.startswith("utm_")]
            )

            gen_qr_with_logo(
                output_file=str(dir / utm),
                target_url=f"{utms[utm]['href']}?{utm_params}",
                logo_path=logo_path,
            )

            gen_qr(
                output_file=str(dir / utm),
                target_url=f"{utms[utm]['href']}?{utm_params}",
            )
            print(f"✅ QR code generated for {utm}!")
