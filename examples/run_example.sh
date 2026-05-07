# Example: Run ERA5 forcing for UIC case

# Set your CDS API key
export CDSAPI_KEY="your-key-here"

# Set project root
export CROCUS_ROOT="/path/to/CROCUS-UES3"

# Run from container directory
cd containers/crocus-forcing

# Build container (first time only)
./build.sh

# Run forcing processing
./run.sh --case uic --output /data/run/uic/forcing

# Or with explicit dates
./run.sh --source era5 --case mycase \
    --start 2024-07-01 --end 2024-07-06 \
    --lat 41.87 --lon -87.65 --z0 177 \
    --output /data/run/mycase/forcing