# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # SST Gap-Filling: Does the WGS84 Ellipsoid Improve Results?
#
# Sea-surface temperature (SST) observations from passive microwave (PMW)
# satellites contain gaps due to cloud cover, land, and sea-ice masking.
# Gap-filling with scattering-transform synthesis (FOSCAT) typically uses
# standard HEALPix, which assumes a perfect sphere.
#
# The Earth is not a sphere -- it is an oblate ellipsoid best described by
# WGS84. The `healpix-geo` and `healpix-resample` packages let us run
# HEALPix on the WGS84 ellipsoid instead.
#
# **Research question:** Does accounting for the WGS84 ellipsoid geometry
# when resampling SST data to HEALPix improve the accuracy of FOSCAT
# gap-filling compared to the standard spherical assumption?
#
# **Method:**
# 1. Download L3S (gappy) and L4 (reference) SST from Copernicus Marine.
# 2. Resample both to HEALPix using (a) sphere and (b) WGS84 ellipsoid.
# 3. Run FOSCAT synthesis to fill gaps in L3S.
# 4. Compare RMSE of gap-filled vs L4 reference for each geometry.

# %%
import os
import warnings
import time
import json

import numpy as np
import healpy as hp
import matplotlib
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# %% [markdown]
# ## Configuration
#
# We use lower resolution and fewer synthesis steps in CI to keep runtime
# short. Set `CI_MODE=1` to activate.

# %%
DATE = "2026-04-01"

CI_MODE = os.environ.get("CI_MODE", "0") == "1"

if CI_MODE:
    NSIDE = 16
    LEVEL = 4       # HEALPix level for healpix-resample (2^level = NSIDE)
    NSTEPS = 20
    LMAX = 15
    print("Running in CI mode (low resolution)")
else:
    NSIDE = 32
    LEVEL = 5
    NSTEPS = 300
    LMAX = 30
    print("Running in full-resolution mode")

NPIX = hp.nside2npix(NSIDE)
print(f"NSIDE={NSIDE}, LEVEL={LEVEL}, NPIX={NPIX}, NSTEPS={NSTEPS}, LMAX={LMAX}")

# %% [markdown]
# ## Data Loading
#
# We download two Copernicus Marine SST products:
# - **L3S** (Level 3 Super-collated): multi-sensor PMW daily, with gaps.
# - **L4** (Level 4): gap-free optimally-interpolated analysis (our reference).

# %%
import copernicusmarine

def load_sst_data(date_str):
    """Download L3S and L4 SST for a single day."""
    date_start = date_str
    date_end = date_str

    # L3S -- gappy PMW observations
    ds_l3s = copernicusmarine.open_dataset(
        dataset_id="cmems_obs-sst_glo_phy_l3s_pmw_P1D-m",
        variables=["sea_surface_temperature"],
        minimum_longitude=-180,
        maximum_longitude=180,
        minimum_latitude=-90,
        maximum_latitude=90,
        start_datetime=f"{date_start}T00:00:00",
        end_datetime=f"{date_end}T23:59:59",
    )

    # L4 -- gap-free reference
    ds_l4 = copernicusmarine.open_dataset(
        dataset_id="cmems_obs-sst_glo_phy-temp_nrt_P1D-m",
        variables=["analysed_sst"],
        minimum_longitude=-180,
        maximum_longitude=180,
        minimum_latitude=-90,
        maximum_latitude=90,
        start_datetime=f"{date_start}T00:00:00",
        end_datetime=f"{date_end}T23:59:59",
    )

    return ds_l3s, ds_l4


ds_l3s, ds_l4 = load_sst_data(DATE)
print(f"L3S shape: {ds_l3s['sea_surface_temperature'].shape}")
print(f"L4  shape: {ds_l4['analysed_sst'].shape}")

# %% [markdown]
# ### Regrid L3S to L4 grid if needed
#
# The two products may be on different grids. We regrid L3S onto the L4
# lat/lon grid using nearest-neighbour interpolation so that both share
# the same 2-D structure before HEALPix resampling.

# %%
import xarray as xr

sst_l4_2d = ds_l4["analysed_sst"].isel(time=0).values  # (lat, lon)
mask_l4 = ~np.isnan(sst_l4_2d)

# Check if grids match
l3s_lat = ds_l3s.lat.values
l4_lat = ds_l4.lat.values
l3s_lon = ds_l3s.lon.values
l4_lon = ds_l4.lon.values

if l3s_lat.shape != l4_lat.shape or not np.allclose(l3s_lat, l4_lat, atol=0.01):
    print("Grids differ -- regridding L3S to L4 grid via interp")
    ds_l3s_regrid = ds_l3s.interp(lat=l4_lat, lon=l4_lon, method="nearest")
    sst_l3s_2d = ds_l3s_regrid["sea_surface_temperature"].isel(time=0).values
else:
    print("Grids match")
    sst_l3s_2d = ds_l3s["sea_surface_temperature"].isel(time=0).values

print(f"L3S 2D: {sst_l3s_2d.shape}, NaN fraction: {np.isnan(sst_l3s_2d).mean():.2%}")
print(f"L4  2D: {sst_l4_2d.shape},  NaN fraction: {np.isnan(sst_l4_2d).mean():.2%}")

# %% [markdown]
# ## Resampling to HEALPix
#
# We use `healpix_resample.GroupByResampler` which supports both standard
# spherical HEALPix and WGS84-ellipsoid HEALPix via the `ellipsoid`
# parameter.

# %%
from healpix_resample import GroupByResampler


def resample_to_healpix(data_2d, mask_2d, lat, lon, ellipsoid="sphere"):
    """
    Resample a 2-D lat/lon array to HEALPix.

    Parameters
    ----------
    data_2d : ndarray (nlat, nlon)
        SST values; NaN where missing.
    mask_2d : ndarray (nlat, nlon)
        Boolean ocean mask (True = ocean).
    lat, lon : 1-D arrays
        Latitude and longitude vectors.
    ellipsoid : str
        "sphere" or "WGS84".

    Returns
    -------
    hp_map : ndarray (npix,)
        HEALPix map with NaN for empty pixels.
    """
    lon_grid, lat_grid = np.meshgrid(lon, lat)
    valid = mask_2d & ~np.isnan(data_2d)

    lon_deg = lon_grid[valid].ravel()
    lat_deg = lat_grid[valid].ravel()
    values = data_2d[valid].ravel()

    resampler = GroupByResampler(
        lon_deg=lon_deg,
        lat_deg=lat_deg,
        level=LEVEL,
        reduce="mean",
        ellipsoid=ellipsoid,
    )
    hp_partial = resampler.fit_transform(values)

    # Build full-size map
    hp_map = np.full(NPIX, np.nan)
    pixel_indices = resampler.pixel_indices_
    hp_map[pixel_indices] = hp_partial

    return hp_map

# %% [markdown]
# ## FOSCAT Synthesis
#
# We define a function that:
# 1. Resamples L4 and L3S to HEALPix with the chosen ellipsoid.
# 2. Identifies ocean, observed, and cloud-gap pixels.
# 3. Computes a spherical-harmonics baseline for the gaps.
# 4. Runs FOSCAT scattering-transform synthesis to fill the gaps.
# 5. Evaluates RMSE against the L4 reference on the gap pixels.

# %%
import foscat.scat_cov as sc
import foscat.Synthesis as synth


def run_foscat(ellipsoid="sphere"):
    """
    Full gap-filling pipeline for a given ellipsoid.

    Returns
    -------
    result : dict
        Keys: ellipsoid, rmse_mk, time_s, hp_l4, hp_l3s, hp_filled, gap_mask
    """
    print(f"\n{'='*60}")
    print(f"  Running FOSCAT with ellipsoid = {ellipsoid}")
    print(f"{'='*60}")
    t0 = time.time()

    # --- 1. Resample to HEALPix ---
    lat = ds_l4.lat.values
    lon = ds_l4.lon.values

    hp_l4 = resample_to_healpix(sst_l4_2d, mask_l4, lat, lon, ellipsoid=ellipsoid)
    hp_l3s = resample_to_healpix(sst_l3s_2d, mask_l4, lat, lon, ellipsoid=ellipsoid)

    ocean = ~np.isnan(hp_l4)
    observed = ~np.isnan(hp_l3s)
    clouds = ocean & ~observed  # gap pixels (ocean but not observed)

    n_ocean = ocean.sum()
    n_obs = observed.sum()
    n_gap = clouds.sum()
    print(f"  Ocean pixels:    {n_ocean}")
    print(f"  Observed pixels: {n_obs}")
    print(f"  Gap pixels:      {n_gap} ({100*n_gap/n_ocean:.1f}%)")

    # --- 2. Spherical-harmonics baseline for gaps ---
    hp_start = hp_l3s.copy()
    # Fill NaN with 0 for alm computation
    hp_for_alm = np.where(np.isnan(hp_start), 0.0, hp_start)

    alm = hp.map2alm(hp_for_alm, lmax=LMAX)
    baseline = hp.alm2map(alm, NSIDE, verbose=False)

    # Use baseline to fill gap pixels as initial guess
    hp_start[clouds] = baseline[clouds]
    # Set non-ocean pixels to 0
    hp_start[~ocean] = 0.0

    print(f"  Spherical-harmonics baseline computed (LMAX={LMAX})")

    # --- 3. FOSCAT synthesis ---
    # Compute scattering covariance of reference (L4)
    hp_l4_clean = hp_l4.copy()
    hp_l4_clean[np.isnan(hp_l4_clean)] = 0.0

    scat_op = sc.funct(NORIENT=4, KERNELSZ=3, all_type="float64")
    ref_cov = scat_op.eval(hp_l4_clean)

    # Define loss mask: we want to match statistics everywhere on ocean
    loss_mask = ocean.astype("float64")

    # Run synthesis
    synthesizer = synth.Synthesis(
        scat_operator=scat_op,
        target_cov=ref_cov,
        image_init=hp_start,
        mask=loss_mask,
        fix_mask=(~clouds).astype("float64"),  # fix non-gap pixels
        n_step=NSTEPS,
    )
    hp_filled = synthesizer.run()

    elapsed = time.time() - t0

    # --- 4. RMSE on gap pixels ---
    diff = hp_filled[clouds] - hp_l4[clouds]
    rmse = np.sqrt(np.nanmean(diff ** 2))
    rmse_mk = rmse * 1000  # convert K to mK

    print(f"  RMSE on gaps: {rmse_mk:.1f} mK")
    print(f"  Elapsed time: {elapsed:.1f} s")

    return {
        "ellipsoid": ellipsoid,
        "rmse_mk": float(rmse_mk),
        "time_s": float(elapsed),
        "n_ocean": int(n_ocean),
        "n_observed": int(n_obs),
        "n_gaps": int(n_gap),
        "hp_l4": hp_l4,
        "hp_l3s": hp_l3s,
        "hp_filled": hp_filled,
        "gap_mask": clouds,
    }

# %% [markdown]
# ## Run both geometries

# %%
r_sphere = run_foscat("sphere")
r_wgs84 = run_foscat("WGS84")

# %% [markdown]
# ## Results comparison

# %%
print("\n" + "=" * 60)
print("  Results Summary")
print("=" * 60)
print(f"{'Geometry':<12} {'RMSE (mK)':>10} {'Time (s)':>10} {'Gaps':>8}")
print("-" * 44)
print(f"{'sphere':<12} {r_sphere['rmse_mk']:>10.1f} {r_sphere['time_s']:>10.1f} {r_sphere['n_gaps']:>8d}")
print(f"{'WGS84':<12} {r_wgs84['rmse_mk']:>10.1f} {r_wgs84['time_s']:>10.1f} {r_wgs84['n_gaps']:>8d}")
print("-" * 44)

diff_mk = r_sphere["rmse_mk"] - r_wgs84["rmse_mk"]
if diff_mk > 0:
    print(f"WGS84 improves RMSE by {diff_mk:.1f} mK ({100*diff_mk/r_sphere['rmse_mk']:.1f}%)")
elif diff_mk < 0:
    print(f"Sphere is better by {-diff_mk:.1f} mK ({100*(-diff_mk)/r_wgs84['rmse_mk']:.1f}%)")
else:
    print("No difference between sphere and WGS84")

# %% [markdown]
# ## Save results

# %%
results_dict = {
    "date": DATE,
    "nside": NSIDE,
    "level": LEVEL,
    "nsteps": NSTEPS,
    "lmax": LMAX,
    "ci_mode": CI_MODE,
    "sphere": {
        "rmse_mk": r_sphere["rmse_mk"],
        "time_s": r_sphere["time_s"],
        "n_ocean": r_sphere["n_ocean"],
        "n_observed": r_sphere["n_observed"],
        "n_gaps": r_sphere["n_gaps"],
    },
    "wgs84": {
        "rmse_mk": r_wgs84["rmse_mk"],
        "time_s": r_wgs84["time_s"],
        "n_ocean": r_wgs84["n_ocean"],
        "n_observed": r_wgs84["n_observed"],
        "n_gaps": r_wgs84["n_gaps"],
    },
    "diff_mk": float(diff_mk),
}

results_path = os.path.join("results", "comparison_results.json")
os.makedirs("results", exist_ok=True)
with open(results_path, "w") as f:
    json.dump(results_dict, f, indent=2)
print(f"Results saved to {results_path}")

# %% [markdown]
# ## Comparison bar chart

# %%
fig, ax = plt.subplots(figsize=(6, 4))
labels = ["Sphere", "WGS84"]
rmses = [r_sphere["rmse_mk"], r_wgs84["rmse_mk"]]
colors = ["#4878CF", "#D65F5F"]

bars = ax.bar(labels, rmses, color=colors, width=0.5, edgecolor="black", linewidth=0.8)

for bar, val in zip(bars, rmses):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.5,
        f"{val:.1f}",
        ha="center",
        va="bottom",
        fontsize=12,
        fontweight="bold",
    )

ax.set_ylabel("RMSE (mK)", fontsize=12)
ax.set_title(f"SST Gap-Filling RMSE: Sphere vs WGS84\n{DATE}, NSIDE={NSIDE}", fontsize=13)
ax.set_ylim(0, max(rmses) * 1.25)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

fig.tight_layout()
chart_path = os.path.join("results", "comparison_rmse.png")
fig.savefig(chart_path, dpi=150)
plt.show()
print(f"Chart saved to {chart_path}")

# %% [markdown]
# ## Credits
#
# - **Jean-Marc Delouis** -- FOSCAT scattering-transform synthesis,
#   healpix-geo, and healpix-resample packages.
#   Reference: Delouis et al. (2022), *Astronomy & Astrophysics*,
#   [DOI:10.1051/0004-6361/202244566](https://doi.org/10.1051/0004-6361/202244566)
# - **Anne Fouilloux** -- LifeWatch ERIC, experiment design and SST
#   application.
# - **FIESTA-OSCARS** -- Funding and project framework.
#
# **Note:** Running this notebook requires valid Copernicus Marine Service
# credentials. Set `COPERNICUSMARINE_SERVICE_USERNAME` and
# `COPERNICUSMARINE_SERVICE_PASSWORD` as environment variables, or
# configure via `copernicusmarine login`.
