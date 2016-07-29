from __future__ import division, absolute_import
import logging

import numpy as np
import matplotlib.pyplot as plt
from pylab import rcParams
from .utils import raster_to_image

logger = logging.getLogger(__name__)


def make_plot(source, reference, target,
              src_arr, ref_arr, tar_arr,
              output, bands):
    """ Create a diagnostic plot showing source, reference and matched image
    and the cumulative distribution functions for each band
    """
    rcParams['figure.figsize'] = 16, 14

    logger.debug("reading images")
    i1 = raster_to_image(source)
    i2 = raster_to_image(reference)
    i3 = raster_to_image(target)

    f, ((ax1, ax2, ax3), (ax4, ax5, ax6), (ax7, ax8, ax9)) = plt.subplots(3, 3)

    logger.debug("showing images")
    ax1.imshow(i1)
    ax1.set_title('Source')
    ax1.set_xticklabels([])
    ax1.set_yticklabels([])

    ax2.imshow(i2)
    ax2.set_title('Reference')
    ax2.set_xticklabels([])
    ax2.set_yticklabels([])

    ax3.imshow(i3)
    ax3.set_title('Matched to ' + ', '.join(str(b) for _, b in bands))
    ax3.set_xticklabels([])
    ax3.set_yticklabels([])

    logger.debug("RGB histograms")
    axes = (ax4, ax5, ax6)
    imgs = (i1, i2, i3)
    titles = ('Source', 'Reference', 'Output')
    bins = 32
    for i, axis in enumerate(axes):
        im = imgs[i]
        title = titles[i]
        # compressed for masked arrays, ravel for ndarray
        red, _ = np.histogram(im[:, :, 0].compressed(), bins, [0, 1])
        green, _ = np.histogram(im[:, :, 1].compressed(), bins, [0, 1])
        blue, _ = np.histogram(im[:, :, 2].compressed(), bins, [0, 1])
        for color, name in ((red, "red"), (green, "green"), (blue, "blue")):
            norm = color / im.size
            # axis.plot(norm, color=name, lw=2)
            axis.fill_between([float(x) / bins for x in range(bins)],
                              norm, facecolor=name, alpha=0.15)
        axis.set_title("{} RGB histogram".format(title))
        # axis.set_yticklabels([])
        axis.grid('on')

    logger.debug("CDF match plots")
    axes = (ax7, ax8, ax9)
    for b, band in bands:
        ax = axes[b]
        source_band = src_arr[b]
        reference_band = ref_arr[b]
        target_band = tar_arr[b]
        try:
            source_band = source_band.compressed()
        except:
            pass

        try:
            reference_band = reference_band.compressed()
        except:
            pass

        try:
            target_band = target_band.compressed()
        except:
            pass

        sv, sc = np.unique(source_band, return_counts=True)
        rv, rc = np.unique(reference_band, return_counts=True)
        tv, tc = np.unique(target_band, return_counts=True)

        scdf = np.cumsum(sc).astype(np.float64) / source_band.size
        rcdf = np.cumsum(rc).astype(np.float64) / reference_band.size
        tcdf = np.cumsum(tc).astype(np.float64) / target_band.size

        ax.set_title("{} cumulative distribution".format(band))
        ax.plot(sv, scdf, label="Source")
        ax.plot(rv, rcdf, label="Reference")
        ax.plot(tv, tcdf, '--r', lw=2, label="Match")
        if b == 1:
            ax.legend(loc=9, bbox_to_anchor=(0.5, -0.05))
        # ax.set_yticklabels([])
        ax.grid('on')

    plt.savefig(output, bbox_inches='tight')
