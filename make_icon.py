from PIL import Image


def generate_icon(input_image_path, output_icon_path):
    # Open the master image
    img = Image.open(input_image_path)

    # The standard sizes Windows/OS needs
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

    # Save directly as .ico
    # The 'append_images' isn't needed for .ico save in PIL if you pass 'sizes'
    # but passing the image itself with the specific sizes ensures high quality resampling.
    img.save(
        output_icon_path,
        format='ICO',
        sizes=icon_sizes
    )

    print(f"Success! {output_icon_path} created with sizes: {icon_sizes}")


if __name__ == "__main__":
    generate_icon("shield_master.png", "game_icon.ico")