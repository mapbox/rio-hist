import numpy as np
import rasterio
from rio_color.colorspace import arr_rgb_to_lch
from rio_color.colorspace import arr_lch_to_rgb
from skimage.color import rgb2lab, lab2rgb
from skimage.color import rgb2hsv, hsv2rgb
from skimage.color import rgb2luv, luv2rgb
from skimage.color import rgb2xyz, xyz2rgb


def reshape_as_image(arr):
    """raster order (bands, rows, cols) -> image (rows, cols, bands)
    """
    return np.swapaxes(np.swapaxes(arr, 0, 2), 0, 1)


def reshape_as_raster(arr):
    """image order (rows, cols, bands) -> rasterio (bands, rows, cols)
    """
    return np.swapaxes(np.swapaxes(arr, 2, 0), 2, 1)


def cs_forward(arr, cs='rgb'):
    """ RGB (any dtype) to whatevs
    """
    arrnorm_raw = arr.astype('float64') / np.iinfo(arr.dtype).max
    arrnorm = arrnorm_raw[0:3]
    cs = cs.lower()
    if cs == 'rgb':
        return arrnorm
    elif cs == 'lch':
        return arr_rgb_to_lch(arrnorm)
    elif cs == 'lab':
        img = reshape_as_image(arrnorm)
        lab = rgb2lab(img)
        return reshape_as_raster(lab)
    elif cs == 'hsv':
        img = reshape_as_image(arrnorm)
        lab = rgb2hsv(img)
        return reshape_as_raster(lab)
    elif cs == 'luv':
        img = reshape_as_image(arrnorm)
        lab = rgb2luv(img)
        return reshape_as_raster(lab)
    elif cs == 'xyz':
        img = reshape_as_image(arrnorm)
        lab = rgb2xyz(img)
        return reshape_as_raster(lab)


def cs_backward(arr, cs='rgb'):
    """ whatevs to RGB 8-bit
    """
    cs = cs.lower()
    if cs == 'rgb':
        return (arr * 255).astype('uint8')
    elif cs == 'lch':
        rgb = arr_lch_to_rgb(arr)
        return (rgb * 255).astype('uint8')
    elif cs == 'lab':
        lab = reshape_as_image(arr)
        rgb = lab2rgb(lab)
        rgbrast = reshape_as_raster(rgb)
        return (rgbrast * 255).astype('uint8')
    elif cs == 'hsv':
        hsv = reshape_as_image(arr)
        rgb = hsv2rgb(hsv)
        rgbrast = reshape_as_raster(rgb)
        return (rgbrast * 255).astype('uint8')
    elif cs == 'luv':
        luv = reshape_as_image(arr)
        rgb = luv2rgb(luv)
        rgbrast = reshape_as_raster(rgb)
        return (rgbrast * 255).astype('uint8')
    elif cs == 'xyz':
        xyz = reshape_as_image(arr)
        rgb = xyz2rgb(xyz)
        rgbrast = reshape_as_raster(rgb)
        return (rgbrast * 255).astype('uint8')


def raster_to_image(raster):
    """Make an image-ordered 8bit 3-band array
    from a rasterio source
    """
    with rasterio.open(raster) as src:
        arr = src.read()
    return reshape_as_image(cs_forward(arr, 'RGB'))
