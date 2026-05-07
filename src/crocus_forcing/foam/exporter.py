"""
OpenFOAM export utilities for forcing data
"""

from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import xarray as xr

from crocus_forcing.base import ForcingData


class FoamExporter:
    """Export forcing data to OpenFOAM-compatible formats"""

    def __init__(self):
        self.vlist = ['thl', 'qt', 'u', 'v', 'w', 'p',
                      'dthldt_advec', 'dqtdt_advec',
                      'dudt_advec', 'dvdt_advec', 'ug', 'vg']
        self.v_sfc_list = ['ps', 'ts']

    def export(self, forcing: ForcingData, output_dir: Path, config: Dict[str, Any]):
        """
        Export ForcingData to all foam-compatible formats.

        Args:
            forcing: Processed ForcingData
            output_dir: Directory to write outputs
            config: Configuration dictionary
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        self.to_forcing_table(forcing, output_dir, config)
        self.to_initial_values(forcing, output_dir, config)
        self.to_netcdf(forcing, output_dir, config)

    def to_forcing_table(self, forcing: ForcingData, output_dir: Path,
                         config: Dict[str, Any]):
        """
        Export to OpenFOAM forcingTable format.

        Output format:
            sourceHeightsMomentum
            (10.0 30.0 ...);
            thl
            ((0.0 val ...) (3600.0 val ...) ...);
            ...
        """
        ds = forcing.dataset
        z = ds.z.values + forcing.z0
        t = ds.time_sec.values

        case_name = config.get("case_name", "forcing")

        lst2foam = lambda lst: f"({(' '.join([str(i) for i in lst]))})"

        lines = []
        lines.append(f"sourceHeightsMomentum\n{lst2foam(z)};")

        for var in self.vlist:
            if var in ds:
                arr = ds[var].values
                lines.append(f"{var}")
                lines.append("(")
                for i in range(t.size):
                    row_data = list(arr[i, :])
                    lines.append(lst2foam([t[i]] + row_data))
                lines.append(");")
            else:
                lines.append(f"{var}")
                lines.append("();")
                lines.append(");")

        forcing_table_path = output_dir / f"forcingTable_{case_name}"
        with open(forcing_table_path, 'w') as f:
            f.write("\n".join(lines) + "\n")

    def to_initial_values(self, forcing: ForcingData, output_dir: Path,
                         config: Dict[str, Any]):
        """
        Export to OpenFOAM initialValues format.

        Output format (per line):
            (z u v thl qt)
        """
        ds = forcing.dataset
        z = ds.z.values + forcing.z0

        u = ds['u'].values[0, :]
        v = ds['v'].values[0, :]
        thl = ds['thl'].values[0, :]
        qt = ds['qt'].values[0, :]

        case_name = config.get("case_name", "forcing")
        initial_values_path = output_dir / f"initialValues_{case_name}"

        with open(initial_values_path, 'w') as f:
            for i in range(z.size):
                f.write(f"({z[i]} {u[i]} {v[i]} {thl[i]} {qt[i]})\n")

    def to_netcdf(self, forcing: ForcingData, output_dir: Path,
                  config: Dict[str, Any]):
        """
        Export to NetCDF with metadata.
        """
        ds = forcing.dataset.copy()
        ds.attrs["case_name"] = forcing.case_name
        ds.attrs["source_type"] = forcing.source_type
        ds.attrs["z0"] = forcing.z0

        if "lat" in config and "lon" in config:
            ds.attrs["central_lat"] = config["lat"]
            ds.attrs["central_lon"] = config["lon"]

        case_name = config.get("case_name", "forcing")
        nc_path = output_dir / f"forcing_export_{case_name}.nc"
        ds.to_netcdf(nc_path)