"""
ERA5 client for downloading data from CDS API
"""

import os
import time
from pathlib import Path
from typing import Dict, Any
import cdsapi
from datetime import datetime


class ERA5Client:
    """Client for downloading ERA5 data from Climate Data Store API"""

    def __init__(self):
        self.cds_url = os.environ.get("CDSAPI_URL", "https://cds.climate.copernicus.eu/api")
        self.cds_key = os.environ.get("CDSAPI_KEY", "")

    def _validate_config(self, config: Dict[str, Any]):
        """Validate required configuration keys"""
        required = ["start_date", "end_date", "central_lat", "central_lon"]
        for key in required:
            if key not in config:
                raise ValueError(f"Missing required config: {key}")

        if not self.cds_key:
            raise ValueError("CDSAPI_KEY environment variable not set")

    def download(self, config: Dict[str, Any], output_dir: Path) -> Path:
        """
        Download ERA5 data from CDS API with retry logic.

        Args:
            config: Configuration dictionary
            output_dir: Directory to store downloaded data

        Returns:
            Path to downloaded ERA5 data directory
        """
        self._validate_config(config)

        import ls2d
        settings = self._to_ls2d_settings(config)
        settings["era5_path"] = str(output_dir)

        case_name = config.get("case_name", "era5_forcing")
        case_dir = output_dir / case_name
        case_dir.mkdir(parents=True, exist_ok=True)

        max_retries = config.get("max_retries", 10)
        retry_interval = config.get("retry_interval", 600)

        for attempt in range(max_retries):
            try:
                ls2d.download_era5(settings)
                return case_dir
            except SystemExit:
                if attempt < max_retries - 1:
                    time.sleep(retry_interval)
                else:
                    raise RuntimeError(f"Failed to download ERA5 after {max_retries} attempts")
        return case_dir

    def read(self, data_path: Path, config: Dict[str, Any]) -> "xr.Dataset":
        """
        Read downloaded ERA5 data using ls2d.

        Args:
            data_path: Path to ERA5 data directory
            config: Configuration dictionary

        Returns:
            xarray Dataset with ERA5 data
        """
        import ls2d
        settings = self._to_ls2d_settings(config)
        settings["era5_path"] = str(data_path)
        era = ls2d.Read_era5(settings)
        return era.data

    def _to_ls2d_settings(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert our config format to ls2d format"""
        start = config["start_date"]
        end = config["end_date"]

        if isinstance(start, str):
            start = datetime.fromisoformat(start)
        if isinstance(end, str):
            end = datetime.fromisoformat(end)

        return {
            "central_lat": config["central_lat"],
            "central_lon": config["central_lon"],
            "area_size": config.get("area_size", 1),
            "case_name": config.get("case_name", "era5_forcing"),
            "era5_expver": config.get("era5_expver", 1),
            "start_date": start,
            "end_date": end,
            "write_log": config.get("write_log", False),
            "data_source": config.get("data_source", "CDS"),
        }