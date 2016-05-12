import logging

import numpy as np

logger = logging.getLogger(__name__)


def histogram_match(source, reference, plot_name=None):
    """
    Adjust the values of a source array
    so that its histogram matches that of a reference array

    Parameters:
    -----------
        source: np.ndarray
        reference: np.ndarray

    Returns:
    -----------
        target: np.ndarray
            The output array with the same shape as source
            but adjusted so that its histogram matches the reference
    """
    orig_shape = source.shape
    source = source.ravel()

    if np.ma.is_masked(reference):
        logger.debug("ref is masked, compressing")
        reference = reference.compressed()
    else:
        logger.debug("ref is unmasked, raveling")
        reference = reference.ravel()

    # get the set of unique pixel values
    # and their corresponding indices and counts
    logger.debug("Get unique pixel values")
    s_values, s_idx, s_counts = np.unique(
        source, return_inverse=True, return_counts=True)
    r_values, r_counts = np.unique(reference, return_counts=True)
    s_size = source.size

    if np.ma.is_masked(source):
        logger.debug("source is masked; get mask_index and remove masked values")
        mask_index = np.ma.where(s_values.mask)
        s_size = np.ma.where(s_idx != mask_index[0])[0].size
        s_values = s_values.compressed()
        s_counts = np.delete(s_counts, mask_index)

    # take the cumsum of the counts; empirical cumulative distribution
    logger.debug("calculate cumulative distribution")
    s_quantiles = np.cumsum(s_counts).astype(np.float64) / s_size
    r_quantiles = np.cumsum(r_counts).astype(np.float64) / reference.size

    # find values in the reference corresponding to the quantiles in the source
    logger.debug("interpolate values from source to reference by cdf")
    interp_r_values = np.interp(s_quantiles, r_quantiles, r_values)

    if np.ma.is_masked(source):
        logger.debug("source is masked, add fill_value back at mask_index")
        interp_r_values = np.insert(interp_r_values, mask_index[0], source.fill_value)

    # using the inverted source indicies, pull out the interpolated pixel values
    logger.debug("create target array from interpolated values by index")
    target = interp_r_values[s_idx]

    if np.ma.is_masked(source):
        logger.debug("source is masked, remask those pixels by position index")
        target = np.ma.masked_where(s_idx == mask_index[0], target)
        target.fill_value = source.fill_value

    return target.reshape(orig_shape)
