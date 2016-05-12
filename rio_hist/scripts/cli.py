import click

import numpy as np
import rasterio
from rasterio.rio.options import creation_options
from rio_hist.utils import cs_forward, cs_backward
from rio_hist.plot import make_plot
from rio_hist.match import histogram_match


@click.command('hist')
# @click.option('--out-dtype', '-d', type=click.Choice(['uint8', 'uint16']),
#               help="Integer data type for output data, default: same as input")
@click.option('--color-space', '-c', default="RGB",
              type=click.Choice(['RGB', 'HSV', 'LCH', 'LAB', 'LUV', 'XYZ']),
              help="Colorspace")
@click.option('--bands', '-b', default="1,2,3",
              help="comma-separated list of bands to match (default 1,2,3)")
@click.option('--plot', is_flag=True, default=False,
              help="create a <basename>_plot.jpg with diagnostic plots")
@click.argument('src_path', type=click.Path(exists=True))
@click.argument('ref_path', type=click.Path(exists=True))
@click.argument('dst_path', type=click.Path(exists=False))
@click.pass_context
@creation_options
def hist(ctx, src_path, ref_path, dst_path,
         creation_options, bands, color_space, plot):
    """Color correction by histogram matching
    """
    with rasterio.open(src_path) as src:
        profile = src.profile.copy()
        profile['transform'] = profile['affine']
        src_arr = src.read(masked=True)

        _msk = src_arr.mask
        if _msk.sum() == 0:
            src_mask = None
            src_fill = None
        else:
            # TODO use alpha instead if available
            src_mask = (_msk[0] & _msk[1] & _msk[2])
            src_fill = src_arr.fill_value
        src_arr = src_arr.filled()  # to ndarray, mask re-applied later

    with rasterio.open(ref_path) as ref:
        ref_arr = ref.read(masked=True)

        _msk = ref_arr.mask
        if _msk.sum() == 0:
            ref_mask = None
            ref_fill = None
        else:
            # TODO use alpha instead if available
            ref_mask = (_msk[0] & _msk[1] & _msk[2])
            ref_fill = ref_arr.fill_value
        ref_arr = ref_arr.filled()  # to ndarray, mask re-applied later

    src = cs_forward(src_arr, color_space)
    ref = cs_forward(ref_arr, color_space)

    bixs = tuple([int(x) - 1 for x in bands.split(',')])
    band_names = [color_space[x] for x in bixs]  # assume 1 letter per band

    target = src.copy()
    for i, b in enumerate(bixs):
        src_band = src[b]
        ref_band = ref[b]

        # Re-apply 2D mask to each band
        if src_mask is not None and src_fill:
            src_band = np.ma.asarray(src_band)
            src_band.mask = src_mask
            src_band.fill_value = src_fill

        if ref_mask is not None and ref_fill:
            ref_band = np.ma.asarray(ref_band)
            # ref_band.mask = np.array((ref_mask, ref_mask, ref_mask))
            ref_band.mask = ref_mask
            ref_band.fill_value = ref_fill

        target[b] = histogram_match(src_band, ref_band)

    target_rgb = cs_backward(target, color_space)

    profile['dtype'] = 'uint8'
    with rasterio.open(dst_path, 'w', **profile) as dst:

        # re-apply src_mask to target_rgb and write ndv
        if not np.ma.is_masked(target_rgb):
            target_rgb = np.ma.asarray(target_rgb)
        target_rgb.mask = np.array((src_mask, src_mask, src_mask))
        target_rgb.fill_value = src_fill

        dst.write(target_rgb)

    if plot:
        make_plot(
            src_path, ref_path, dst_path,
            src, ref, target,
            output=dst_path + "_plot.jpg",
            bands=tuple(zip(bixs, band_names)))
