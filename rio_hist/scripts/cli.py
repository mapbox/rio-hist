import click

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
        src_arr = src.read()

    with rasterio.open(ref_path) as ref:
        ref_arr = ref.read()

    src = cs_forward(src_arr, color_space)
    ref = cs_forward(ref_arr, color_space)

    bixs = tuple([int(x) - 1 for x in bands.split(',')])
    band_names = [color_space[x] for x in bixs]  # assume 1 letter per band

    target = src.copy()
    for i, b in enumerate(bixs):
        target[b] = histogram_match(src[b], ref[b])

    target_rgb = cs_backward(target, color_space)

    profile['dtype'] = 'uint8'
    with rasterio.open(dst_path, 'w', **profile) as dst:
        dst.write(target_rgb)

    if plot:
        make_plot(
            src_path, ref_path, dst_path,
            src, ref, target,
            output=dst_path + "_plot.jpg",
            bands=tuple(zip(bixs, band_names)))
