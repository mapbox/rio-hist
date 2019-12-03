from __future__ import division, absolute_import
import warnings

import numpy as np
import rasterio
from rasterio.enums import ColorInterp, MaskFlags
from rio_color.colorspace import convert_arr, ColorSpace


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


def read_mask(dataset):
    """Get the dataset's mask

    Returns
    -------
    numpy.array

    Notes
    -----
    This function is no longer called by module code but we're going to
    continue to test it for a few future versions as insurance on the new
    implementation.

    """
    return dataset.dataset_mask()
