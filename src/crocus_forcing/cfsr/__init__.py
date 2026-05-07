"""
CFSR forcing data source - stub for future implementation
"""

from crocus_forcing.base import ForcingSource, ForcingData
from pathlib import Path
from typing import Dict, Any


class CFSRForcing(ForcingSource):
    """CFSR forcing - not yet implemented"""

    def download(self, config: Dict[str, Any], output_dir: Path) -> Path:
        raise NotImplementedError("CFSR forcing not yet implemented")

    def read(self, data_path: Path, config: Dict[str, Any]):
        raise NotImplementedError("CFSR forcing not yet implemented")

    def process(self, data, config: Dict[str, Any]) -> ForcingData:
        raise NotImplementedError("CFSR forcing not yet implemented")

    def export(self, forcing: ForcingData, output_dir: Path, config: Dict[str, Any]):
        raise NotImplementedError("CFSR forcing not yet implemented")