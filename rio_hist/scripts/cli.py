import logging
import os

import click
import numpy as np
import rasterio
from rasterio.rio.options import creation_options
from rio_hist.utils import cs_forward, cs_backward
from rio_hist.plot import make_plot
from rio_hist.match import histogram_match

logger = logging.getLogger('rio_hist')

@click.command('hist')
@click.option('--color-space', '-c', default="RGB",
              type=click.Choice(['RGB', 'HSV', 'LCH', 'LAB', 'LUV', 'XYZ']),
              help="Colorspace")
@click.option('--bands', '-b', default="1,2,3",
              help="comma-separated list of bands to match (default 1,2,3)")
@click.option('--plot', is_flag=True, default=False,
              help="create a <basename>_plot.jpg with diagnostic plots")
@click.option('--verbose', '-v', is_flag=True, default=False)
@click.argument('src_path', type=click.Path(exists=True))
@click.argument('ref_path', type=click.Path(exists=True))
@click.argument('dst_path', type=click.Path(exists=False))
@click.pass_context
@creation_options
def hist(ctx, src_path, ref_path, dst_path,
         verbose, creation_options, bands, color_space, plot):
    """Color correction by histogram matching
    """
    if verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("Matching {} to histogram of {} using {} color space".format(
        os.path.basename(src_path), os.path.basename(ref_path), color_space))

    with rasterio.open(src_path) as src:
        profile = src.profile.copy()

        src_arr = src.read(masked=True)
        _msk = src_arr.mask
        if _msk.sum() == 0:
            logger.debug("src has all valid data, no mask needed")
            src_mask = None
            src_fill = None
        else:
            logger.debug("src has nodata pixels, calculating mask")
            # TODO alpha band? gdal mask? union of 3 bands?
            # IOW how to get the definitive 2D mask?
            src_mask = (_msk[0] & _msk[1] & _msk[2])
            src_fill = src_arr.fill_value
        # to ndarray, mask re-applied later
        src_arr = src_arr.filled()

    with rasterio.open(ref_path) as ref:
        ref_arr = ref.read(masked=True)
        _msk = ref_arr.mask
        if _msk.sum() == 0:
            logger.debug("ref has all valid data, no mask needed")
            ref_mask = None
            ref_fill = None
        else:
            logger.debug("ref has nodata pixels, calculating mask")
            # TODO alpha band? gdal mask? union of 3 bands?
            # IOW how to get the definitive 2D mask?
            ref_mask = (_msk[0] & _msk[1] & _msk[2])
            ref_fill = ref_arr.fill_value
        # to ndarray, mask re-applied later
        ref_arr = ref_arr.filled()

    src = cs_forward(src_arr, color_space)
    ref = cs_forward(ref_arr, color_space)

    bixs = tuple([int(x) - 1 for x in bands.split(',')])
    band_names = [color_space[x] for x in bixs]  # assume 1 letter per band

    target = src.copy()
    for i, b in enumerate(bixs):
        logger.debug("Processing band {}".format(b))
        src_band = src[b]
        ref_band = ref[b]

        # Re-apply 2D mask to each band
        if src_mask is not None and src_fill is not None:
            logger.debug("apply src_mask to band {}".format(b))
            src_band = np.ma.asarray(src_band)
            src_band.mask = src_mask
            src_band.fill_value = src_fill

        if ref_mask is not None and ref_fill is not None:
            logger.debug("apply ref_mask to band {}".format(b))
            ref_band = np.ma.asarray(ref_band)
            ref_band.mask = ref_mask
            ref_band.fill_value = ref_fill

        target[b] = histogram_match(src_band, ref_band)

    target_rgb = cs_backward(target, color_space)

    # re-apply src_mask to target_rgb and write ndv
    if src_mask is not None:
        logger.debug("apply src_mask to target_rgb")
        if not np.ma.is_masked(target_rgb):
            target_rgb = np.ma.asarray(target_rgb)
        target_rgb.mask = np.array((src_mask, src_mask, src_mask))
        target_rgb.fill_value = src_fill

    profile['dtype'] = 'uint8'
    profile['transform'] = profile['affine']
    profile.update(creation_options)

    logger.info("Writing raster {}".format(dst_path))
    with rasterio.open(dst_path, 'w', **profile) as dst:
        dst.write(target_rgb)

    if plot:
        outplot = os.path.splitext(dst_path)[0] + "_plot.jpg"
        logger.info("Writing figure to {}".format(outplot))
        make_plot(
            src_path, ref_path, dst_path,
            src, ref, target,
            output=outplot,
            bands=tuple(zip(bixs, band_names)))
