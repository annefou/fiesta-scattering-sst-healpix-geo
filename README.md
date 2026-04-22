# SST Gap-Filling: Sphere vs WGS84 Ellipsoid on HEALPix

Does accounting for the WGS84 ellipsoid geometry when resampling sea-surface
temperature (SST) data to HEALPix improve the accuracy of scattering-transform
gap-filling compared to the standard spherical assumption?

## Overview

Passive microwave SST observations (Copernicus Marine L3S) contain gaps from
cloud cover, land masking, and sea-ice. We fill these gaps using
[FOSCAT](https://github.com/jmdelouis/foscat) (Forward Scattering Covariance
Analysis Tool) on HEALPix grids and compare two geometries:

- **Sphere** -- standard HEALPix (perfect sphere)
- **WGS84** -- HEALPix on the WGS84 ellipsoid via
  [healpix-geo](https://github.com/jmdelouis/healpix-geo) and
  [healpix-resample](https://github.com/jmdelouis/healpix-resample)

We evaluate gap-filled SST against the Copernicus Marine L4 analysis (gap-free
reference) using RMSE on the gap pixels.

## Method

1. Download L3S (gappy) and L4 (reference) SST from Copernicus Marine Service.
2. Resample both products to HEALPix using (a) sphere and (b) WGS84 ellipsoid.
3. Run FOSCAT scattering-transform synthesis to fill gaps in L3S.
4. Compute RMSE of gap-filled result vs L4 on gap-only pixels.

## Quick start

```bash
# Clone
git clone https://github.com/annefou/fiesta-scattering-sst-healpix-geo.git
cd fiesta-scattering-sst-healpix-geo

# Create environment
conda env create -f environment.yml
conda activate fiesta-sst-healpix

# Set Copernicus Marine credentials
export COPERNICUSMARINE_SERVICE_USERNAME="your-username"
export COPERNICUSMARINE_SERVICE_PASSWORD="your-password"

# Run the experiment
snakemake --cores 1

# Or run the notebook directly
jupytext --to notebook 01_sphere_vs_wgs84.py
jupyter execute 01_sphere_vs_wgs84.ipynb
```

## Docker

```bash
docker build -t fiesta-sst-healpix .
docker run --rm \
  -e COPERNICUSMARINE_SERVICE_USERNAME \
  -e COPERNICUSMARINE_SERVICE_PASSWORD \
  -v $(pwd)/results:/app/results \
  fiesta-sst-healpix
```

## Repository structure

```
.
├── 01_sphere_vs_wgs84.py   # Jupytext notebook (percent format)
├── environment.yml          # Conda environment
├── Dockerfile               # Reproducible container
├── Snakefile                # Workflow manager
├── myst.yml                 # MyST configuration for Jupyter Book
├── index.md                 # Jupyter Book landing page
├── results/                 # Output directory (charts, JSON)
├── CITATION.cff             # Citation metadata
├── codemeta.json            # CodeMeta software metadata
├── LICENSE                  # MIT License
└── .github/workflows/       # CI/CD
    ├── run-experiment.yml   # Run experiment on push
    └── jupyter-book.yml     # Build and deploy Jupyter Book
```

## References

Delouis, J.-M. et al. (2022). "Scattering transform applied to CMB
component separation." *Astronomy & Astrophysics*, 668, A122.
[DOI:10.1051/0004-6361/202244566](https://doi.org/10.1051/0004-6361/202244566)

## Credits

- **Jean-Marc Delouis** -- FOSCAT, healpix-geo, healpix-resample
- **Anne Fouilloux** -- LifeWatch ERIC, experiment design
- **FIESTA-OSCARS** -- Funding and project framework

## License

MIT License. See [LICENSE](LICENSE).
