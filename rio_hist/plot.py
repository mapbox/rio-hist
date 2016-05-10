import numpy as np
import matplotlib.pyplot as plt
from pylab import rcParams
from .utils import raster_to_image


def make_plot(source, reference, target,
              src_arr, ref_arr, tar_arr,
              output, bands):
    """ Create a diagnostic plot showing source, reference and matched image
    and the cumulative distribution functions for each band
    """
    rcParams['figure.figsize'] = 16, 14

    i1 = raster_to_image(source)
    i2 = raster_to_image(reference)
    i3 = raster_to_image(target)

    f, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3)

    ax1.imshow(i1)
    ax1.set_title('Source')
    ax2.imshow(i2)
    ax2.set_title('Reference')
    ax3.imshow(i3)
    ax3.set_title('Matched to ' + ', '.join(str(b) for _, b in bands))
    axes = (ax4, ax5, ax6)

    for b, band in bands:
        ax = axes[b]
        source_band = src_arr[b]
        reference_band = ref_arr[b]
        target_band = tar_arr[b]

        sv, sc = np.unique(source_band, return_counts=True)
        rv, rc = np.unique(reference_band, return_counts=True)
        tv, tc = np.unique(target_band, return_counts=True)

        scdf = np.cumsum(sc).astype(np.float64) / source_band.size
        rcdf = np.cumsum(rc).astype(np.float64) / reference_band.size
        tcdf = np.cumsum(tc).astype(np.float64) / target_band.size

        ax.set_title("{} cdf match".format(band))
        ax.plot(sv, scdf, label="Source")
        ax.plot(rv, rcdf, label="Reference")
        ax.plot(tv, tcdf, '--r', lw=2, label="Match")
        ax.legend(loc=9, bbox_to_anchor=(0.5, -0.05))
        ax.grid('on')

    plt.savefig(output)
