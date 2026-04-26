# SST Gap-Filling: Sphere vs WGS84 Ellipsoid on HEALPix

[![Source DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19693573.svg)](https://doi.org/10.5281/zenodo.19693573)
[![Docker image DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19707991.svg)](https://doi.org/10.5281/zenodo.19707991)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

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

## FORRT nanopublication chain

The full provenance of this question-rooted study is recorded as a six-step
FORRT nanopublication chain on the
[Science Live](https://platform.sciencelive4all.org) platform. Each step is
independently citable and machine-readable; together they form the FAIR
provenance receipt for this study.

> **Headline assertion — machine-readable:**
> [**This work `cito:extends` the chain #3 sphere baseline, `cito:usesMethodIn` Delouis et al. 2022, AND `cito:credits` the IGARSS 2024 Pangeo tutorial**](https://w3id.org/sciencelive/np/RAFe7IfYuLYqNUYbtxUrRmk2D5JhyoWJjwY5iytqdzM5g)
>
> The CiTO citation nanopublication encodes three relationships at once:
> this work extends the [`fiesta-scattering-sst`](https://github.com/annefou/fiesta-scattering-sst)
> sphere-only baseline to operational resolution with a paired
> sphere-vs-WGS84 comparison (`cito:extends`); the underlying
> scattering-transform method comes from Delouis et al. 2022
> (`cito:usesMethodIn`); and the operational SST workflow we follow is
> from Jean-Marc Delouis's IGARSS 2024 Pangeo tutorial (`cito:credits`).
> Discovery tools (Scholia, Wikidata pipelines, SPARQL endpoints) can
> follow this single citation to find all three relationships.

The five preceding nanopubs build the provenance ladder up to that citation:

| Step | Type | Asserts | Nanopub URI |
|---|---|---|---|
| 1 | PCC Research Question | The research question itself: does WGS84 ellipsoid geometry improve scattering-transform SST gap-filling vs the spherical assumption? | [`RA9hv…`](https://w3id.org/sciencelive/np/RA9hvGhxFk1QOqFhSAUKzWbIyE0sdRduQgQOIzdVZvHJo) |
| 2 | AIDA sentence *(Nanodash namespace)* | Declarative answer: using WGS84 ellipsoid geometry instead of perfect-sphere HEALPix improves scattering-transform SST gap-filling accuracy at operational resolution. *(Published via Nanodash because of a Science Live AIDA-form bug with combined datasets+publications fields.)* | [`RA0P2…`](https://w3id.org/np/RA0P2dPFtPiyzW7uHgmAf_nBcwnUtAEYYpDV1Wkko8dC4) |
| 3 | FORRT Claim (data quality) | The geometry-choice claim, typed as a FORRT data-quality claim — testing whether a data-preparation step (HEALPix resampling) preserves fidelity better under one geometry than another | [`RAMDV…`](https://w3id.org/sciencelive/np/RAMDVUPB2XRLXYwtggM0GXIRqhavuPaaRHmVezbsxtdS0) |
| 4 | FORRT Replication Study | Single-day comparison of sphere vs WGS84 at HEALPix nside=128, on Copernicus Marine SST 2026-04-01, with L4 as ground truth | [`RA0vq…`](https://w3id.org/sciencelive/np/RA0vq7OGc7G5we208CYmsu_3De-9IY0BN0yCLcXYBGBFA) |
| 5 | FORRT Replication Outcome (Validated, Moderate) | Sphere RMSE 1333.0 mK; WGS84 RMSE 1165.3 mK; WGS84 reduces RMSE by 167.7 mK (12.6%) at operational resolution | [`RAs--…`](https://w3id.org/sciencelive/np/RAs--Uf0wMFAWeTv54c4P37QYNp70c8nxUY9M6HgOfg4c) |
| 6 | **CiTO citation — `cito:extends` chain #3 + `cito:usesMethodIn` Delouis 2022 + `cito:credits` IGARSS 2024 tutorial** | The headline triple assertion above | [**`RAFe7…`**](https://w3id.org/sciencelive/np/RAFe7IfYuLYqNUYbtxUrRmk2D5JhyoWJjwY5iytqdzM5g) |

The chain runs: research question → declarative claim → FORRT claim →
study (this repo) → outcome (the RMSE comparison) → CiTO citations to
the three relationships above.

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

## Note on FOSCAT and GPU/CPU support

The [FOSCAT](https://github.com/jmdelouis/FOSCAT) package (as of v2026.2.7 on
PyPI) has several hardcoded `device='cuda'` defaults, which means it **only
works on machines with an NVIDIA GPU** out of the box. On CPU-only machines
(Apple Silicon Macs, CI runners, etc.) it will crash with a CUDA device error.

We have submitted a fix upstream:
[jmdelouis/FOSCAT#40](https://github.com/jmdelouis/FOSCAT/pull/40)
([commit](https://github.com/annefou/FOSCAT/commit/04244ed)).

Until the fix is merged and released, you can install FOSCAT from our fork:

```bash
pip install git+https://github.com/annefou/FOSCAT.git@v0.1.0-cpu
```

The fix is fully backwards compatible: on CUDA machines the behaviour is
identical to the original. It simply adds auto-detection so that CPU is used as
a fallback when CUDA is not available.

## References

Delouis, J.-M. et al. (2022). "Scattering transform applied to CMB
component separation." *Astronomy & Astrophysics*, 668, A122.
[DOI:10.1051/0004-6361/202244566](https://doi.org/10.1051/0004-6361/202244566)

## Container image

A Docker container is built on every release, pushed to GitHub Container
Registry, and archived to Zenodo.

```bash
docker pull ghcr.io/annefou/fiesta-scattering-sst-healpix-geo:latest
docker run --rm -v "$PWD/results:/app/results" \
    -e COPERNICUSMARINE_SERVICE_USERNAME=... \
    -e COPERNICUSMARINE_SERVICE_PASSWORD=... \
    ghcr.io/annefou/fiesta-scattering-sst-healpix-geo:latest
```

Zenodo-archived tarballs via the
[Docker image concept DOI 10.5281/zenodo.19707991](https://doi.org/10.5281/zenodo.19707991).

## How to cite

```
Fouilloux, A. (2026). SST Gap-Filling: Sphere vs WGS84 Ellipsoid on HEALPix
(v0.2.1). Zenodo. https://doi.org/10.5281/zenodo.19693573
```

BibTeX:

```bibtex
@software{fouilloux_fiesta_scattering_sst_healpix_geo,
  author    = {Fouilloux, Anne},
  title     = {SST Gap-Filling: Sphere vs WGS84 Ellipsoid on HEALPix},
  year      = {2026},
  version   = {0.2.1},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.19693573},
  url       = {https://doi.org/10.5281/zenodo.19693573}
}
```

The DOI above is the **concept DOI** — it always resolves to the latest
release. See [`CITATION.cff`](CITATION.cff) for machine-readable citation
metadata.

## Credits

- **Jean-Marc Delouis** -- FOSCAT, healpix-geo, healpix-resample
- **Anne Fouilloux** -- LifeWatch ERIC, experiment design
- **FIESTA-OSCARS** -- Funding and project framework

## License

MIT License. See [LICENSE](LICENSE).
