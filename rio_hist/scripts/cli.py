import logging

import click
from rasterio.rio.options import creation_options
from rio_hist.match import hist_match_worker

logger = logging.getLogger('rio_hist')


def validate_proportion(ctx, param, value):
    if value < 0 or value > 1:
        raise click.BadParameter('must be between 0 and 1')
    return float(value)


@click.command('hist')
@click.option('--color-space', '-c', default="RGB",
              type=click.Choice(['RGB', 'LCH', 'LAB', 'Lab', 'LUV', 'XYZ']),
              help="Colorspace")
@click.option('--bands', '-b', default="1,2,3",
              help="comma-separated list of bands to match (default 1,2,3)")
@click.option('--match-proportion', '-m', default=1.0, type=float,
              callback=validate_proportion,
              help="Interpolate values between source and reference histogram. "
                   "1.0 (default) is full match, 0.0 is no match")
@click.option('--plot', is_flag=True, default=False,
              help="create a <basename>_plot.png with diagnostic plots")
@click.option('--verbose', '-v', is_flag=True, default=False)
@click.argument('src_path', type=click.Path(exists=True))
@click.argument('ref_path', type=click.Path(exists=True))
@click.argument('dst_path', type=click.Path(exists=False))
@click.pass_context
@creation_options
def hist(ctx, src_path, ref_path, dst_path, match_proportion,
         verbose, creation_options, bands, color_space, plot):
    """Color correction by histogram matching
    """
    if verbose:
        logger.setLevel(logging.DEBUG)

    hist_match_worker(src_path, ref_path, dst_path, match_proportion,
                      creation_options, bands, color_space, plot)
