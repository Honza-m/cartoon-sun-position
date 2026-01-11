import os

from PIL import Image

from cartoon_sun_position.constants import OUTPUT_DIR


def save_image(canvas: Image.Image):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = OUTPUT_DIR / "final.png"
    canvas.save(out_path)


def show_image(canvas: Image.Image):
    canvas.show()


def save_images_as_gif(frames: list[Image.Image], duration=200):
    frames = [f.convert("RGBA") for f in frames]
    frames[0].save(
        OUTPUT_DIR / "output.gif",
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
    )
