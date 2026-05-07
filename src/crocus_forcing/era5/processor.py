"""
ERA5 processor using ls2d for forcing calculations
"""

from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import xarray as xr

from crocus_forcing.base import ForcingData, ForcingSource
from crocus_forcing.era5.client import ERA5Client


class ERA5Processor:
    """Processor for ERA5 data using ls2d methodology"""

    def __init__(self):
        self.client = ERA5Client()

    def calculate_forcings(self, data: xr.Dataset, config: Dict[str, Any]) -> xr.Dataset:
        """
        Calculate large-scale forcings from ERA5 data.

        Args:
            data: Raw ERA5 xarray Dataset
            config: Configuration dictionary with processing options

        Returns:
            Dataset with calculated forcing fields
        """
        import ls2d

        settings = self.client._to_ls2d_settings(config)

        era = ls2d.Read_era5(settings)
        era.data = data

        n_av = config.get("n_av", 1)
        method = config.get("method", "2nd")
        era.calculate_forcings(n_av=n_av, method=method)

        return era.data

    def get_les_input(self, data: xr.Dataset, config: Dict[str, Any]) -> xr.Dataset:
        """
        Extract LES input fields at specified heights.

        Args:
            data: ERA5 Dataset after calculate_forcings
            config: Configuration dictionary with 'heights' list

        Returns:
            Dataset with LES input at specified heights
        """
        import ls2d

        settings = self.client._to_ls2d_settings(config)
        era = ls2d.Read_era5(settings)
        era.data = data

        heights = config.get("heights", np.arange(10, 2000, 20))
        les_input = era.get_les_input(heights)

        return self._rename_for_foam(les_input)

    def _rename_for_foam(self, les_input: xr.Dataset) -> xr.Dataset:
        """Rename variables to foam-compatible names"""
        rename_map = {
            "dtthl_advec": "dthldt_advec",
            "dtqt_advec": "dqtdt_advec",
            "dtu_advec": "dudt_advec",
            "dtv_advec": "dvdt_advec",
            "wls": "w"
        }
        existing = {k: v for k, v in rename_map.items() if k in les_input}
        return les_input.rename(existing)

    def process(self, data: xr.Dataset, config: Dict[str, Any]) -> ForcingData:
        """
        Full processing pipeline: calculate_forcings -> get_les_input.

        Args:
            data: Raw ERA5 Dataset
            config: Configuration dictionary

        Returns:
            ForcingData with processed LES input
        """
        with_forcings = self.calculate_forcings(data, config)
        les_input = self.get_les_input(with_forcings, config)

        z0 = config.get("z0", 0.0)

        return ForcingData(
            dataset=les_input,
            case_name=config.get("case_name", "era5_forcing"),
            source_type="era5",
            z0=z0
        )


class ERA5Forcing(ForcingSource):
    """Complete ERA5 forcing source implementation"""

    def __init__(self):
        self.client = ERA5Client()
        self.processor = ERA5Processor()

    def download(self, config: Dict[str, Any], output_dir: Path) -> Path:
        return self.client.download(config, output_dir)

    def read(self, data_path: Path, config: Dict[str, Any]) -> xr.Dataset:
        return self.client.read(data_path, config)

    def process(self, data: xr.Dataset, config: Dict[str, Any]) -> ForcingData:
        return self.processor.process(data, config)

    def export(self, forcing: ForcingData, output_dir: Path, config: Dict[str, Any]):
        from crocus_forcing.era5.exporter import FoamExporter
        exporter = FoamExporter()
        exporter.export(forcing, output_dir, config)