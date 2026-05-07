"""
ERA5-specific configuration helpers
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ERA5Config:
    """Configuration for ERA5 forcing"""
    central_lat: float
    central_lon: float
    start_date: datetime
    end_date: datetime
    case_name: str = "era5_forcing"
    area_size: float = 1.0
    era5_expver: int = 1
    data_source: str = "CDS"
    z0: float = 0.0
    heights: List[float] = None
    n_av: int = 1
    method: str = "2nd"

    def __post_init__(self):
        if self.heights is None:
            self.heights = list(range(10, 2000, 20))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "central_lat": self.central_lat,
            "central_lon": self.central_lon,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "case_name": self.case_name,
            "area_size": self.area_size,
            "era5_expver": self.era5_expver,
            "data_source": self.data_source,
            "z0": self.z0,
            "heights": self.heights,
            "n_av": self.n_av,
            "method": self.method,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ERA5Config":
        if isinstance(d["start_date"], str):
            d["start_date"] = datetime.fromisoformat(d["start_date"])
        if isinstance(d["end_date"], str):
            d["end_date"] = datetime.fromisoformat(d["end_date"])
        return cls(**d)