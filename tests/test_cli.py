import os

from click.testing import CliRunner
import pytest
import rasterio

from rio_hist.scripts.cli import hist


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
