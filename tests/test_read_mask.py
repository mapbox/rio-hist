import numpy as np
import rasterio
from affine import Affine
from rio_hist.utils import read_mask


red = np.array([[0, 0, 0],
                [0, 1, 1],
                [1, 0, 1]]).astype('uint8') * 255

grn = np.array([[0, 0, 0],
                [1, 0, 1],
                [1, 0, 1]]).astype('uint8') * 255

blu = np.array([[0, 0, 0],
                [1, 1, 0],
                [1, 0, 1]]).astype('uint8') * 255

alp = red | grn | blu
# equivalent to
# 255 anywhere there is at least on r g b value
# alp = np.array([[0, 0, 0]
#                 [1, 1, 1],
#                 [1, 0, 1]]).astype('uint8') * 255

# mask might be constructed using different tools
# and differ from a strict interpretation of rgb values
msk = np.array([[0, 0, 0],
                [1, 1, 1],
                [1, 1, 1]]).astype('uint8') * 255

alldata = np.array([[1, 1, 1],
                    [1, 1, 1],
                    [1, 1, 1]]).astype('uint8') * 255


_profile = {
    'affine': Affine(5.0, 0.0, 0.0, 0.0, -5.0, 0.0),
    'transform': Affine(5.0, 0.0, 0.0, 0.0, -5.0, 0.0),
    'crs': {'init': 'epsg:4326'},
    'driver': 'GTiff',
    'dtype': 'uint8',
    'height': 3,
    'width': 3}

# 1. RGB without nodata value
prof = _profile.copy()
prof['count'] = 3
prof['nodata'] = None
with rasterio.open('/tmp/rgb_no_ndv.tif', 'w', **prof) as dst:
    dst.write(red, 1)
    dst.write(grn, 2)
    dst.write(blu, 3)

# 2. RGB with nodata value
prof = _profile.copy()
prof['count'] = 3
prof['nodata'] = 0
with rasterio.open('/tmp/rgb_ndv.tif', 'w', **prof) as dst:
    dst.write(red, 1)
    dst.write(grn, 2)
    dst.write(blu, 3)

# 3. RGBA without nodata value
prof = _profile.copy()
prof['count'] = 4
prof['nodata'] = None
with rasterio.open('/tmp/rgba_no_ndv.tif', 'w', **prof) as dst:
    dst.write(red, 1)
    dst.write(grn, 2)
    dst.write(blu, 3)
    dst.write(alp, 4)

# 4. RGBA with nodata value
prof = _profile.copy()
prof['count'] = 4
prof['nodata'] = 0
with rasterio.open('/tmp/rgba_ndv.tif', 'w', **prof) as dst:
    dst.write(red, 1)
    dst.write(grn, 2)
    dst.write(blu, 3)
    dst.write(alp, 4)

# 5. RGB with msk
prof = _profile.copy()
prof['count'] = 3
with rasterio.open('/tmp/rgb_msk.tif', 'w', **prof) as dst:
    dst.write(red, 1)
    dst.write(grn, 2)
    dst.write(blu, 3)
    dst.write_mask(msk)

# 6. RGB with msk (internal)
prof = _profile.copy()
prof['count'] = 3
with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=True) as env:
    with rasterio.open('/tmp/rgb_msk_internal.tif', 'w', **prof) as dst:
        dst.write(red, 1)
        dst.write(grn, 2)
        dst.write(blu, 3)
        dst.write_mask(msk)

# 7. RGBA with msk
prof = _profile.copy()
prof['count'] = 4
with rasterio.open('/tmp/rgba_msk.tif', 'w', **prof) as dst:
    dst.write(red, 1)
    dst.write(grn, 2)
    dst.write(blu, 3)
    dst.write(alp, 4)
    dst.write_mask(msk)


def test_no_ndv():
    with rasterio.open('/tmp/rgb_no_ndv.tif') as src:
        assert np.array_equal(read_mask(src), alldata)

def test_rgb_ndv():
    with rasterio.open('/tmp/rgb_ndv.tif') as src:
        assert np.array_equal(read_mask(src), alp)

def test_rgba_no_ndv():
    with rasterio.open('/tmp/rgba_no_ndv.tif') as src:
        assert np.array_equal(read_mask(src), alp)

def test_rgba_ndv():
    with rasterio.open('/tmp/rgba_ndv.tif') as src:
        assert np.array_equal(read_mask(src), alp)

def test_rgb_msk():
    with rasterio.open('/tmp/rgb_msk.tif') as src:
        assert np.array_equal(read_mask(src), msk)
        # each band's mask is also equal
        for bmask in src.read_masks():
            assert np.array_equal(bmask, msk)

def test_rgb_msk_int():
    with rasterio.open('/tmp/rgb_msk_internal.tif') as src:
        assert np.array_equal(read_mask(src), msk)

def test_rgba_msk():
    with rasterio.open('/tmp/rgba_msk.tif') as src:
        # mask takes precendent over alpha
        assert np.array_equal(read_mask(src), msk)
