from __future__ import division, absolute_import
import warnings

import numpy as np
import rasterio
from rasterio.enums import ColorInterp, MaskFlags
from rio_color.colorspace import convert_arr, ColorSpace


def read_mask(src):
    """
    TODO Use RasterReader.dataset_mask in rasterio 0.36
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

    TODO Use rasterio.plot.reshape_as_image in rasterio 0.36?
    """
    return np.swapaxes(np.swapaxes(arr, 0, 2), 0, 1)


def reshape_as_raster(arr):
    """image order (rows, cols, bands) -> rasterio (bands, rows, cols)

    TODO Use rasterio.plot.reshape_as_image in rasterio 0.36?
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
        return convert_arr(arrnorm,
                           src=ColorSpace.rgb,
                           dst=ColorSpace.lch)
    elif cs == 'lab':
        return convert_arr(arrnorm,
                           src=ColorSpace.rgb,
                           dst=ColorSpace.lab)
    elif cs == 'luv':
        return convert_arr(arrnorm,
                           src=ColorSpace.rgb,
                           dst=ColorSpace.luv)
    elif cs == 'xyz':
        return convert_arr(arrnorm,
                           src=ColorSpace.rgb,
                           dst=ColorSpace.xyz)


def cs_backward(arr, cs='rgb'):
    """ whatevs to RGB 8-bit
    """
    cs = cs.lower()
    if cs == 'rgb':
        return (arr * 255).astype('uint8')
    elif cs == 'lch':
        rgb = convert_arr(arr,
                          src=ColorSpace.lch,
                          dst=ColorSpace.rgb)
        return (rgb * 255).astype('uint8')
    elif cs == 'lab':
        rgb = convert_arr(arr,
                          src=ColorSpace.lab,
                          dst=ColorSpace.rgb)
        return (rgb * 255).astype('uint8')
    elif cs == 'luv':
        rgb = convert_arr(arr,
                          src=ColorSpace.luv,
                          dst=ColorSpace.rgb)
        return (rgb * 255).astype('uint8')
    elif cs == 'xyz':
        rgb = convert_arr(arr,
                          src=ColorSpace.xyz,
                          dst=ColorSpace.rgb)
        return (rgb * 255).astype('uint8')


def raster_to_image(raster):
    """Make an image-ordered 8bit 3-band array
    from a rasterio source
    """
    with rasterio.open(raster) as src:
        arr = src.read(masked=True)
    return reshape_as_image(cs_forward(arr, 'RGB'))
