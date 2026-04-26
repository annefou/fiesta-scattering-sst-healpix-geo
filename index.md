---
title: "SST Gap-Filling: Sphere vs WGS84 Ellipsoid on HEALPix"
---

# SST Gap-Filling: Does the WGS84 Ellipsoid Improve Results?

This project investigates whether accounting for the WGS84 ellipsoid geometry
when resampling sea-surface temperature (SST) data to HEALPix improves the
accuracy of gap-filling with scattering-transform synthesis (FOSCAT).

## Motivation

Standard HEALPix assumes the Earth is a perfect sphere. In reality, the Earth
is an oblate ellipsoid (equatorial radius ~21 km larger than polar). The
[healpix-geo](https://github.com/jmdelouis/healpix-geo) and
[healpix-resample](https://github.com/jmdelouis/healpix-resample) packages
extend HEALPix to the WGS84 ellipsoid.

For CMB analysis on the celestial sphere, the spherical assumption is exact.
For Earth-observation data like SST, the mismatch between sphere and ellipsoid
could introduce systematic biases in pixel areas and neighbour relationships,
potentially degrading gap-filling quality.

## Experiment

We compare FOSCAT gap-filling RMSE (vs Copernicus Marine L4 reference) using:

1. **Sphere** -- standard HEALPix pixelisation
2. **WGS84** -- HEALPix on the WGS84 ellipsoid

See the full analysis in {doc}`01_sphere_vs_wgs84`.

## FORRT nanopublication chain

The full provenance of this question-rooted study is recorded as a six-step
FORRT nanopublication chain on the
[Science Live](https://platform.sciencelive4all.org) platform — research
question → declarative answer → FORRT claim → study → outcome → CiTO
citations. Each step is independently citable and machine-readable.

> **Headline assertion — machine-readable:**
> [**This work `cito:extends` chain #3 (`fiesta-scattering-sst`), `cito:usesMethodIn` Delouis et al. 2022, AND `cito:credits` the IGARSS 2024 Pangeo tutorial**](https://w3id.org/sciencelive/np/RAFe7IfYuLYqNUYbtxUrRmk2D5JhyoWJjwY5iytqdzM5g)
>
> Three relationships in one citation nanopublication: extends the
> sphere-only baseline at chain #3 to operational resolution with the
> sphere-vs-WGS84 comparison; uses the FOSCAT scattering method from
> Delouis 2022; credits Jean-Marc Delouis's IGARSS 2024 Pangeo tutorial
> as the SST workflow source.

The five preceding nanopubs build the provenance ladder up to that citation:

| Step | Type | Nanopub URI |
|---|---|---|
| 1 | PCC Research Question | <https://w3id.org/sciencelive/np/RA9hvGhxFk1QOqFhSAUKzWbIyE0sdRduQgQOIzdVZvHJo> |
| 2 | AIDA sentence *(Nanodash namespace)* | <https://w3id.org/np/RA0P2dPFtPiyzW7uHgmAf_nBcwnUtAEYYpDV1Wkko8dC4> |
| 3 | FORRT Claim (data quality) | <https://w3id.org/sciencelive/np/RAMDVUPB2XRLXYwtggM0GXIRqhavuPaaRHmVezbsxtdS0> |
| 4 | FORRT Replication Study | <https://w3id.org/sciencelive/np/RA0vq7OGc7G5we208CYmsu_3De-9IY0BN0yCLcXYBGBFA> |
| 5 | FORRT Replication Outcome (Validated, Moderate) | <https://w3id.org/sciencelive/np/RAs--Uf0wMFAWeTv54c4P37QYNp70c8nxUY9M6HgOfg4c> |
| 6 | **CiTO `extends` chain #3 + `usesMethodIn` Delouis 2022 + `credits` IGARSS 2024 tutorial** | **<https://w3id.org/sciencelive/np/RAFe7IfYuLYqNUYbtxUrRmk2D5JhyoWJjwY5iytqdzM5g>** |

## References

- Delouis, J.-M. et al. (2022). *Astronomy & Astrophysics*, 668, A122.
  [DOI:10.1051/0004-6361/202244566](https://doi.org/10.1051/0004-6361/202244566)
