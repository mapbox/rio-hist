import logging

import click
from rasterio.rio.options import creation_options
from rio_hist.match import hist_match_worker

logger = logging.getLogger('rio_hist')


@click.command('hist')
@click.option('--color-space', '-c', default="RGB",
              type=click.Choice(['RGB', 'LCH', 'Lab', 'LUV', 'XYZ']),
              help="Colorspace")
@click.option('--bands', '-b', default="1,2,3",
              help="comma-separated list of bands to match (default 1,2,3)")
@click.option('--plot', is_flag=True, default=False,
              help="create a <basename>_plot.png with diagnostic plots")
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

    hist_match_worker(src_path, ref_path, dst_path,
                      creation_options, bands, color_space, plot)
