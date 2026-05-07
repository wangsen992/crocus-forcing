"""
Base classes for forcing data sources
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List
import xarray as xr


@dataclass
class ForcingData:
    """Container for processed forcing data"""
    dataset: xr.Dataset
    case_name: str
    source_type: str
    z0: float = 0.0

    @property
    def times(self) -> xr.DataArray:
        return self.dataset.time_sec

    @property
    def heights(self) -> xr.DataArray:
        return self.dataset.z

    def to_netcdf(self, path: Path):
        self.dataset.to_netcdf(path)

    @classmethod
    def from_netcdf(cls, path: Path) -> "ForcingData":
        ds = xr.load_dataset(path)
        return cls(
            dataset=ds,
            case_name=ds.attrs.get("case_name", "unknown"),
            source_type=ds.attrs.get("source_type", "unknown"),
            z0=ds.attrs.get("z0", 0.0)
        )


class ForcingSource(ABC):
    """
    Abstract base class for forcing data sources.

    Implement this class to add support for new forcing data sources
    (e.g., ERA5, CFSR, GFS, custom datasets).
    """

    @abstractmethod
    def download(self, config: Dict[str, Any], output_dir: Path) -> Path:
        """
        Download forcing data from source.

        Args:
            config: Configuration dictionary with source-specific settings
            output_dir: Directory to store downloaded data

        Returns:
            Path to downloaded data
        """
        pass

    @abstractmethod
    def read(self, data_path: Path, config: Dict[str, Any]) -> xr.Dataset:
        """
        Read downloaded data into xarray Dataset.

        Args:
            data_path: Path to downloaded data
            config: Configuration dictionary

        Returns:
            xarray Dataset with raw data
        """
        pass

    @abstractmethod
    def process(self, data: xr.Dataset, config: Dict[str, Any]) -> ForcingData:
        """
        Process raw data into forcing data.

        Args:
            data: Raw xarray Dataset from read()
            config: Configuration dictionary

        Returns:
            ForcingData container with processed forcing
        """
        pass

    @abstractmethod
    def export(self, forcing: ForcingData, output_dir: Path, config: Dict[str, Any]):
        """
        Export ForcingData to model-compatible format.

        Args:
            forcing: Processed ForcingData
            output_dir: Directory to write output files
            config: Configuration dictionary
        """
        pass

    def run(self, config: Dict[str, Any], output_dir: Path):
        """
        Full pipeline: download -> read -> process -> export

        Args:
            config: Configuration dictionary
            output_dir: Directory for outputs

        Returns:
            ForcingData result
        """
        data_path = self.download(config, output_dir)
        raw_data = self.read(data_path, config)
        forcing = self.process(raw_data, config)
        self.export(forcing, output_dir, config)
        return forcing