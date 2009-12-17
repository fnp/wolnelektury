from PIL import Image, ImageFilter, ImageChops


def add_padding(image, requested_size, opts):
    if 'pad' in opts:
        padded_image = Image.new('RGBA', requested_size, '#fff')
        width, height = image.size
        requested_width, requested_height = requested_size
        padded_image.paste(image, (0, requested_height - height / 2))
        return padded_image
    return image

add_padding.valid_options = ('pad',)
