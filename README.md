# CROCUS forcing

ERA5 and other forcing data processing for urban CFD simulations.

## Overview

`crocus-forcing` provides a containerized workflow for downloading and processing atmospheric forcing data (ERA5, CFSR, GFS, etc.) into OpenFOAM-compatible formats for LES simulations.

## Repository Structure

```
crocus-forcing/
├── crocus_forcing.def    # Apptainer definition file
├── build.sh              # Build script
├── run.sh                # Run wrapper
├── images/               # Built SIF images
├── src/crocus_forcing/   # Python package
│   ├── base.py          # ForcingSource ABC
│   ├── era5/            # ERA5 implementation
│   ├── cfsr/            # CFSR (future)
│   └── gfs/             # GFS (future)
├── config/               # Case configurations
│   ├── default.yaml
│   └── cases/
├── scripts/              # CLI entry point
└── tests/                # Unit tests
```

## Quick Start

### Build Container

```bash
./build.sh
```

### Run ERA5 Processing

```bash
# Using predefined case config
./run.sh --case uic --output ./forcing

# Using custom config
./run.sh --config config/cases/uic.yaml --output ./forcing

# Using command-line arguments
./run.sh --source era5 --case my_case \
    --start 2024-07-01 --end 2024-07-06 \
    --lat 41.87 --lon -87.65 --z0 177 \
    --output ./forcing
```

## Configuration

Case configurations are stored in `config/cases/`. See `config/cases/template.yaml` for the format.

### UIC Case Example

```yaml
central_lat: 41.8692893
central_lon: -87.6463732
start_date: "2024-07-01T00:00:00"
end_date: "2024-07-06T00:00:00"
case_name: "Forcing_UIC_case0"
era5_expver: 1
z0: 177.0
area_size: 1.0
n_av: 1
method: "2nd"
```

## Output

The processor generates three output files per case:

- `forcingTable_{case_name}` - OpenFOAM forcing table with time-varying 3D fields
- `initialValues_{case_name}` - Initial vertical profiles for U, V, theta, q
- `forcing_export_{case_name}.nc` - NetCDF with full metadata

## Environment Variables

- `CDSAPI_KEY` - Required for ERA5 download from CDS API
- `CROCUS_ROOT` - Project root for path bindings (default: auto-detect)