from sorl.thumbnail.engines import pil_engine
from sorl.thumbnail import parsers

#
# Class developed by 
# http://timmyomahony.com/blog/custom-cropping-engine-sorl-thumbnail/
#
class CustomCroppingEngine(pil_engine.Engine):
    """
    A custom sorl.thumbnail engine (using PIL) that first crops an image
    according to 4 pixel/percentage values in the source image, then scales
    that crop down to the size specified in the geometry. This is in contrast
    to sorl.thumbnails default engine which first scales the image down to the
    specified geometry and applies the crop afterward.
    """
    def create(self, image, geometry, options):
        image = self.orientation(image, geometry, options)
    image = self.colorspace(image, geometry, options)
    image = self.crop(image, geometry, options)
    image = self.scale(image, geometry, options)
    return image

    def _crop_parse(self, crop, xy_image, xy_window):
        """
        Conver the crop string passed by the user to accurate cropping values
        (This is adapter from the default sorl.thumbnail.parsers.parse_crop)
        """
        crops = crop.split(' ')
        if len(crops) != 4:
            raise parsers.ThumbnailParseError('Unrecognized crop option: %s' % crop)
        x1, y1, x2, y2 = crops

        def get_offset(crop, epsilon):
            m = parsers.bgpos_pat.match(crop)
            if not m:
                raise parsers.ThumbnailParseError('Unrecognized crop option: %s' % crop)
            value = int(m.group('value')) # we only take ints in the regexp
            unit = m.group('unit')
            if unit == '%':
                value = epsilon * value / 100.0
                return int(max(0, min(value, epsilon)))
        x1 = get_offset(x1, xy_image[0])
        y1 = get_offset(y1, xy_image[0])
        x2 = get_offset(x2, xy_image[1])
        y2 = get_offset(y2, xy_image[1])
        return x1, y1, x2, y2

    def crop(self, image, geometry, options):
        crop = options['crop']
        if not crop or crop == 'noop':
            return image
        x_image, y_image = self.get_image_size(image)
        x1,y1,x2,y2 = self._crop_parse(crop, (x_image, y_image), geometry)
        return self._crop(image, x1, y1, x2, y2)

    def _crop(self, image, x1, y1, x2, y2):
        return image.crop((x1, y1, x2, y2))
