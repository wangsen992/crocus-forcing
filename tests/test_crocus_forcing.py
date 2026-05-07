import pytest
from pathlib import Path
import numpy as np
import xarray as xr

from crocus_forcing.base import ForcingData, ForcingSource
from crocus_forcing.era5.processor import ERA5Processor
from crocus_forcing.foam.exporter import FoamExporter


class TestForcingData:
    def test_forcing_data_creation(self, tmp_path):
        ds = xr.Dataset({
            'u': xr.DataArray(np.random.rand(10, 5)),
            'v': xr.DataArray(np.random.rand(10, 5)),
        })
        fd = ForcingData(
            dataset=ds,
            case_name="test_case",
            source_type="era5",
            z0=100.0
        )
        assert fd.case_name == "test_case"
        assert fd.source_type == "era5"
        assert fd.z0 == 100.0

    def test_forcing_data_netcdf_roundtrip(self, tmp_path):
        ds = xr.Dataset({
            'thl': xr.DataArray(np.random.rand(10, 5)),
            'qt': xr.DataArray(np.random.rand(10, 5)),
        })
        fd = ForcingData(
            dataset=ds,
            case_name="test",
            source_type="era5"
        )
        nc_path = tmp_path / "test.nc"
        fd.to_netcdf(nc_path)
        assert nc_path.exists()


class TestFoamExporter:
    def test_export_creates_files(self, tmp_path):
        ds = xr.Dataset({
            'z': xr.DataArray(np.arange(10, 100, 20)),
            'time_sec': xr.DataArray([0, 3600]),
            'thl': xr.DataArray(np.random.rand(2, 5)),
            'qt': xr.DataArray(np.random.rand(2, 5)),
            'u': xr.DataArray(np.random.rand(2, 5)),
            'v': xr.DataArray(np.random.rand(2, 5)),
            'w': xr.DataArray(np.random.rand(2, 5)),
            'p': xr.DataArray(np.random.rand(2, 5)),
            'dthldt_advec': xr.DataArray(np.random.rand(2, 5)),
            'dqtdt_advec': xr.DataArray(np.random.rand(2, 5)),
            'dudt_advec': xr.DataArray(np.random.rand(2, 5)),
            'dvdt_advec': xr.DataArray(np.random.rand(2, 5)),
            'ug': xr.DataArray(np.random.rand(2, 5)),
            'vg': xr.DataArray(np.random.rand(2, 5)),
        })
        fd = ForcingData(
            dataset=ds,
            case_name="test",
            source_type="era5",
            z0=0.0
        )
        config = {"case_name": "test"}

        exporter = FoamExporter()
        exporter.export(fd, tmp_path, config)

        assert (tmp_path / "forcingTable_test").exists()
        assert (tmp_path / "initialValues_test").exists()
        assert (tmp_path / "forcing_export_test.nc").exists()

    def test_forcing_table_format(self, tmp_path):
        ds = xr.Dataset({
            'z': xr.DataArray([10, 30, 50]),
            'time_sec': xr.DataArray([0]),
            'thl': xr.DataArray([[296, 297, 298]]),
            'qt': xr.DataArray([[0.01, 0.011, 0.012]]),
            'u': xr.DataArray([[-2, -2.1, -2.2]]),
            'v': xr.DataArray([[1, 1.1, 1.2]]),
            'w': xr.DataArray([[0, 0, 0]]),
            'p': xr.DataArray([[101000, 101000, 101000]]),
            'dthldt_advec': xr.DataArray([[0, 0, 0]]),
            'dqtdt_advec': xr.DataArray([[0, 0, 0]]),
            'dudt_advec': xr.DataArray([[0, 0, 0]]),
            'dvdt_advec': xr.DataArray([[0, 0, 0]]),
            'ug': xr.DataArray([[-5, -5, -5]]),
            'vg': xr.DataArray([[0, 0, 0]]),
        })
        fd = ForcingData(dataset=ds, case_name="test", source_type="era5")

        exporter = FoamExporter()
        exporter.to_forcing_table(fd, tmp_path, {"case_name": "test"})

        content = (tmp_path / "forcingTable_test").read_text()
        assert "sourceHeightsMomentum" in content
        assert "thl" in content


class TestERA5Processor:
    def test_processor_initialization(self):
        proc = ERA5Processor()
        assert proc.client is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])