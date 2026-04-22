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

## References

- Delouis, J.-M. et al. (2022). *Astronomy & Astrophysics*, 668, A122.
  [DOI:10.1051/0004-6361/202244566](https://doi.org/10.1051/0004-6361/202244566)
