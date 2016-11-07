import os

import click
from click.testing import CliRunner
import pytest
import rasterio
import numpy as np

from rio_hist.scripts.cli import hist, validate_proportion


def test_hist_cli(tmpdir):
    output = str(tmpdir.join('matched.tif'))
    runner = CliRunner()
    result = runner.invoke(
        hist, ['tests/data/source1.tif',
               'tests/data/reference1.tif',
               output])
    assert result.exit_code == 0
    assert os.path.exists(output)

def test_hist_cli2(tmpdir):
    output = str(tmpdir.join('matched.tif'))
    runner = CliRunner()
    result = runner.invoke(
        hist, ['tests/data/source2.tif',
               'tests/data/reference2.tif',
               output])
    assert result.exit_code == 0
    with rasterio.open(output) as out:
        assert out.count == 4  # RGBA

def test_hist_cli_lab_colorspace(tmpdir):
    output = str(tmpdir.join('matched.tif'))
    runner = CliRunner()
    result = runner.invoke(
        hist, ['-c', 'Lab', '-b', '1,2,3',
               'tests/data/source1.tif',
               'tests/data/reference1.tif',
               output])
    assert result.exit_code == 0
    assert os.path.exists(output)

def test_hist_cli_lch_colorspace(tmpdir):
    output = str(tmpdir.join('matched.tif'))
    runner = CliRunner()
    result = runner.invoke(
        hist, ['-c', 'LCH', '-b', '1,2,3',
               'tests/data/source1.tif',
               'tests/data/reference1.tif',
               output])
    assert result.exit_code == 0
    assert os.path.exists(output)

def test_hist_cli_luv_colorspace(tmpdir):
    output = str(tmpdir.join('matched.tif'))
    runner = CliRunner()
    result = runner.invoke(
        hist, ['-c', 'LUV', '-b', '1,2,3',
               'tests/data/source1.tif',
               'tests/data/reference1.tif',
               output])
    assert result.exit_code == 0
    assert os.path.exists(output)

def test_hist_cli_xyz_colorspace(tmpdir):
    output = str(tmpdir.join('matched.tif'))
    runner = CliRunner()
    result = runner.invoke(
        hist, ['-c', 'XYZ', '-b', '1,2,3',
               'tests/data/source1.tif',
               'tests/data/reference1.tif',
               output])
    assert result.exit_code == 0
    assert os.path.exists(output)

def test_hist_cli_plot(tmpdir):
    output = str(tmpdir.join('matched.tif'))
    runner = CliRunner()
    result = runner.invoke(
        hist, ['-v', '--plot',
               'tests/data/source2.tif',
               'tests/data/reference2.tif',
               output])
    assert result.exit_code == 0
    with rasterio.open(output) as out:
        assert out.count == 4  # RGBA

def test_partial(tmpdir):
    output = str(tmpdir.join('matched.tif'))
    runner = CliRunner()
    result = runner.invoke(
        hist, ['-m', '0.5',
               'tests/data/source1.tif',
               'tests/data/reference1.tif',
               output])
    assert result.exit_code == 0
    with rasterio.open(output) as match, \
            rasterio.open('tests/data/source1.tif') as src, \
            rasterio.open('tests/data/reference1.tif') as ref:
        m = match.read(2)
        s = src.read(2)
        r = ((ref.read(2) / 65365) * 256).astype('uint8')
        assert np.median(s) > np.median(m)  # darker than the source
        assert np.median(r) < np.median(m)  # but not quite as dark as the reference


def test_validate_proportion():
    assert validate_proportion(None, None, 0) == 0.0
    assert validate_proportion(None, None, 0.5) == 0.5
    assert validate_proportion(None, None, 1) == 1.0
    with pytest.raises(click.BadParameter):
        assert validate_proportion(None, None, 9000)
