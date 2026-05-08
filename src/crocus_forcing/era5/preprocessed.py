"""
Preprocessed ERA5 data source - reads from existing ls2d output files
"""

from pathlib import Path
from typing import Dict, Any
import xarray as xr

from crocus_forcing.base import ForcingData, ForcingSource


class PreprocessedERA5(ForcingSource):
    """
    Read ERA5 forcing data from pre-processed ls2d output files.

    This handles the existing forcing export file format from the original
    ls2d-processed ERA5 data, which has the structure matching OpenFOAM's
    expected forcingTable format.

    Expected file structure:
        forcing_export_{case_name}.nc - xarray Dataset with time/z dimensions
        Contains: thl, qt, u, v, w, p, dthldt_advec, dqtdt_advec,
                  dudt_advec, dvdt_advec, ug, vg

    Example:
        config = {
            'case_name': 'UIC_case0',
            'forcing_export_path': '/path/to/forcing_export_UIC_case0.nc',
            'z0': 177.0,
        }
    """

    def __init__(self):
        pass

    def download(self, config: Dict[str, Any], output_dir: Path) -> Path:
        """Not applicable for preprocessed data"""
        raise NotImplementedError(
            "PreprocessedERA5 does not support downloading. "
            "Use preprocessed forcing export files instead."
        )

    def read(self, data_path: Path, config: Dict[str, Any]) -> xr.Dataset:
        """
        Read preprocessed forcing data from export file.

        Args:
            data_path: Path to directory containing forcing_export_{case_name}.nc
            config: Configuration dictionary

        Returns:
            xarray Dataset with forcing variables
        """
        case_name = config.get("case_name", "forcing")
        export_file = data_path / f"forcing_export_{case_name}.nc"

        if not export_file.exists():
            export_file = data_path / f"forcing_export_{case_name}.nc"

        if not export_file.exists():
            raise FileNotFoundError(
                f"Could not find forcing export file: {export_file}"
            )

        ds = xr.open_dataset(export_file)
        return ds

    def process(self, data: xr.Dataset, config: Dict[str, Any]) -> ForcingData:
        """
        Convert xarray Dataset to ForcingData.

        Args:
            data: xarray Dataset from read()
            config: Configuration dictionary with 'z0' key

        Returns:
            ForcingData object
        """
        z0 = config.get("z0", 0.0)
        case_name = config.get("case_name", "forcing")

        return ForcingData(
            dataset=data,
            case_name=case_name,
            source_type="era5_preprocessed",
            z0=z0
        )

    def export(self, forcing: ForcingData, output_dir: Path, config: Dict[str, Any]):
        """
        Export ForcingData to OpenFOAM formats.

        Args:
            forcing: Processed ForcingData
            output_dir: Directory to write outputs
            config: Configuration dictionary
        """
        from crocus_forcing.foam.exporter import FoamExporter

        exporter = FoamExporter()
        exporter.export(forcing, output_dir, config)