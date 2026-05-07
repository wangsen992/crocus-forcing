#!/bin/bash
# ===========================================
# crocus-forcing Run Script
# ===========================================
#
# Wrapper script to run crocus-forcing inside Apptainer container.
# Handles path bindings and environment for ERA5 processing.
#
# Usage:
#   ./run.sh --case uic --output ./forcing
#   ./run.sh --config config/cases/uic.yaml --output ./forcing
#   ./run.sh --help
#
# Environment Variables:
#   CROCUS_ROOT     Project root (default: auto-detect from script location)
#   CDSAPI_KEY      CDS API key for ERA5 download (required)
#
# Bindings:
#   /data  → CROCUS_ROOT
#   /run   → \$CROCUS_ROOT/run/ (simulation cases)
#
# ===========================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -n "${CROCUS_ROOT}" ]; then
    PROJECT_ROOT="${CROCUS_ROOT}"
else
    PROJECT_ROOT="${SCRIPT_DIR}/../../CROCUS-UES3"
fi

IMAGE_PATH="$SCRIPT_DIR/images/crocus-forcing.sif"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

error() { echo -e "${RED}[ERROR]${NC} $1"; }
info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

show_help() {
    cat << EOF
Usage: ./run.sh [OPTIONS]

Run crocus-forcing inside Apptainer container.

Options:
    --case NAME         Case name (predefined in config/cases/)
    --config FILE      Path to YAML config file
    --source TYPE       Forcing source type (era5, cfsr, gfs)
    --output DIR       Output directory (default: ./forcing)
    --start DATE       Start date (ISO format)
    --end DATE         End date (ISO format)
    --lat LAT          Central latitude
    --lon LON          Central longitude
    --z0 Z0            Terrain elevation offset (meters)
    --shell            Start interactive shell
    --help             Show this help

Examples:
    # Using predefined case config
    ./run.sh --case uic --output /data/run/uic/forcing

    # Using custom config file
    ./run.sh --config /data/config/my_case.yaml --output /data/run/mycase/forcing

    # Using command-line arguments
    ./run.sh --source era5 --case mycase \\
        --start 2024-07-01 --end 2024-07-06 \\
        --lat 41.87 --lon -87.65 --z0 177 \\
        --output /data/run/mycase/forcing

Environment Variables:
    CROCUS_ROOT    Project root directory
    CDSAPI_KEY     CDS API key (required for ERA5 download)

Bindings:
    /data  → CROCUS_ROOT
    /run   → \$CROCUS_ROOT/run/
EOF
}

if [ ! -f "$IMAGE_PATH" ]; then
    error "Image not found: $IMAGE_PATH"
    echo "Run ./build.sh first to build the image."
    exit 1
fi

if [ ! -d "$PROJECT_ROOT" ]; then
    error "Project root not found: $PROJECT_ROOT"
    echo "Set CROCUS_ROOT environment variable to point to your project."
    exit 1
fi

BINDINGS="-B ${PROJECT_ROOT}:/data"
BINDINGS="$BINDINGS -B ${PROJECT_ROOT}/run:/run"

if [ -n "$CDSAPI_KEY" ]; then
    CDS_BINDS="-e CDSAPI_KEY"
fi

if [ "${1:-}" = "--help" ]; then
    show_help
    exit 0
fi

if [ "${1:-}" = "--shell" ]; then
    info "Starting interactive shell..."
    apptainer shell $BINDINGS "$IMAGE_PATH"
else
    apptainer exec $BINDINGS $CDS_BINDS "$IMAGE_PATH" python scripts/run_forcing.py "$@"
fi