import numpy as np
import rasterio
from rasterio.enums import ColorInterp, MaskFlags
from rio_color.colorspace import arr_rgb_to_lch
from rio_color.colorspace import arr_lch_to_rgb
from skimage.color import rgb2lab, lab2rgb
from skimage.color import rgb2hsv, hsv2rgb
from skimage.color import rgb2luv, luv2rgb
from skimage.color import rgb2xyz, xyz2rgb


def read_mask(src):
    """Get the 2D uint8 dataset-wide mask according to these rules, in order of precedence

    1. If a .msk file, dataset-wide alpha or internal mask exists, it will be used for the mask band.
    2. If an 4-band RGB with a shadow nodata value, band 4 will be used as the mask band.
    3. If a nodata value exists, use the binary OR intersection of the band masks
    4. If no nodata value, return a mask with all 255

    0 = nodata, 255 = valid data
    Note that this differs slighly from GDAL RFC15 in that it applies dataset-wide
    (see https://trac.osgeo.org/gdal/wiki/rfc15_nodatabitmask)
    """
    masks = src.read_masks()

    # GDAL found dataset-wide alpha band or mask
    if src.mask_flags[0] & MaskFlags.per_dataset:
        return masks[0]

    # use Alpha mask if available and looks like RGB, even if nodata is shadowing
    elif src.count == 4 and src.colorinterp(1) == ColorInterp.red:
        return masks[3]

    # Or use the binary OR intersection of all GDALGetMaskBands
    else:
        mask = masks[0]
        for i in range(1, src.count):
            mask = mask | masks[i]
        return mask


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
        arr = src.read(masked=True)
    return reshape_as_image(cs_forward(arr, 'RGB'))
