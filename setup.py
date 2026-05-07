from setuptools import setup, find_packages

setup(
    name="crocus-forcing",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "xarray",
        "netcdf4",
        "pandas",
        "pyyaml",
        "scipy",
        "cdsapi",
    ],
    entry_points={
        "console_scripts": [
            "crocus-forcing=scripts.run_forcing:main",
        ],
    },
    author="CROCUS Team",
    description="ERA5 and other forcing data processing for urban CFD",
    url="https://github.com/wangsen992/crocus-forcing",
)