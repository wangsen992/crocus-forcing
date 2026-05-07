#!/usr/bin/env python3
"""
CLI for CROCUS forcing data processing

Usage:
    python run_forcing.py --case uic --output ./forcing
    python run_forcing.py --config config/cases/uic.yaml --output ./forcing
    python run_forcing.py --source era5 --case uic --start 2024-07-01 --end 2024-07-06 --output ./forcing
"""

import argparse
import sys
from pathlib import Path
import yaml

from crocus_forcing.base import ForcingSource
from crocus_forcing.era5.processor import ERA5Forcing


def load_config(config_path: Path) -> dict:
    """Load YAML configuration file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_case_config(case_name: str, config_dir: Path = Path("config/cases")) -> dict:
    """Load a predefined case configuration"""
    case_path = config_dir / f"{case_name}.yaml"
    if not case_path.exists():
        raise FileNotFoundError(f"Case config not found: {case_path}")
    return load_config(case_path)


def get_forcing_source(source_type: str) -> ForcingSource:
    """Get forcing source instance by type"""
    sources = {
        "era5": ERA5Forcing,
    }
    if source_type not in sources:
        raise ValueError(f"Unknown source type: {source_type}. Available: {list(sources.keys())}")
    return sources[source_type]()


def run_era5(args):
    """Run ERA5 forcing processing"""
    if args.config:
        config = load_config(Path(args.config))
    else:
        config = {
            "case_name": args.case,
            "start_date": args.start,
            "end_date": args.end,
            "central_lat": args.lat,
            "central_lon": args.lon,
            "z0": args.z0 or 0.0,
        }

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    source = get_forcing_source(args.source)
    result = source.run(config, output_dir)

    print(f"Forcing data written to: {output_dir}")
    print(f"  - forcingTable_{config['case_name']}")
    print(f"  - initialValues_{config['case_name']}")
    print(f"  - forcing_export_{config['case_name']}.nc")


def main():
    parser = argparse.ArgumentParser(
        description="CROCUS Forcing Data Processing CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with predefined case config
  python run_forcing.py --case uic --output ./forcing

  # Run with custom config file
  python run_forcing.py --config config/cases/uic.yaml --output ./forcing

  # Run with command-line arguments
  python run_forcing.py --source era5 --case my_case \\
      --start 2024-07-01 --end 2024-07-06 \\
      --lat 41.87 --lon -87.65 \\
      --z0 177 --output ./forcing
        """
    )

    parser.add_argument(
        "--source", "-s",
        default="era5",
        choices=["era5", "cfsr", "gfs"],
        help="Forcing data source type (default: era5)"
    )

    parser.add_argument(
        "--case", "-c",
        help="Case name (used with predefined configs)"
    )

    parser.add_argument(
        "--config", "-f",
        help="Path to YAML config file"
    )

    parser.add_argument(
        "--output", "-o",
        default="./forcing",
        help="Output directory (default: ./forcing)"
    )

    parser.add_argument(
        "--start",
        help="Start date (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
    )

    parser.add_argument(
        "--end",
        help="End date (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
    )

    parser.add_argument(
        "--lat",
        type=float,
        help="Central latitude"
    )

    parser.add_argument(
        "--lon",
        type=float,
        help="Central longitude"
    )

    parser.add_argument(
        "--z0",
        type=float,
        help="Terrain elevation offset (meters)"
    )

    args = parser.parse_args()

    if args.config:
        run_era5(args)
    elif args.case and args.start and args.end:
        run_era5(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()