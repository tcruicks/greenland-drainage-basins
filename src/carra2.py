# This script is used to extract single level data from the New generation pan-Arctic regional reanalysis: CARRA2 from 
# ECMWY/Copernicus.  2m surface temperature and surface runoff is extracted.  The downloaded data file contains monthly
# aggregaTED data.
# To work with grib files cfgrib needs to be installed and then specified in xarray commands as the "engine".

import os
import pathlib
import matplotlib
import matplotlib.pyplot as plt
import pyproj
import regionmask
import pandas as pd
import geopandas as gpd
import data_utils
import xarray as xr

home_dir = os.path.join(
    pathlib.Path.home(),
    'earth-analytics',
    'greenland-temperature',
)

basins_path = os.path.join(
    home_dir,
    'data',
    'doi_10_7280_D1WT11__v20190329',
    'Greenland_Basins_PS_v1.4.2.shp',
)

mask_path = os.path.join(
    home_dir,
    "data",
    "basin_mask.nc"
)
carra2_t2m_path = os.path.join(
    home_dir,
    'data',
    'carra2',
    'cara2_greenland_monthly_t2m_1985_2025.grib',
)

carra2_pcp_path = os.path.join(
    home_dir,
    'data',
    'carra2',
    'cara2_greenland_monthly_totprecip_1985_2025.grib',
)

# Name of Output file containing the basin average monthly precipitation for each of the seven basins.
output_path = f"{home_dir}/data/carra2/carra2_monthly_basin_precip.nc"

# Meteorological variable we want to process.
#var_name = 't2m'
var_name = 'tp'

# Open the GRIB dataset using my open_cara2 function.
carra2_ds = data_utils.open_carra2(carra2_pcp_path)
carra2_ds = carra2_ds.assign_coords(
    longitude=(
        ("y", "x"),
        ((carra2_ds.longitude + 180) % 360 - 180).values
    )
)

# Open the basin mask .nc file that is saved locally.
basins_mask_da = xr.open_dataarray(mask_path)

#-------------------------------------------------
# Efficiently process the large basin dataarrays.
#-------------------------------------------------

mask_stacked = basins_mask_da.stack(cell=("y", "x"))
tp_stacked = carra2_ds.tp.stack(cell=("y", "x"))
tp_stacked = tp_stacked.assign_coords(basin=mask_stacked)
tp_grouped = tp_stacked.groupby("basin")
monthly_tp_basin_avg = tp_grouped.mean(dim="cell") * tp_stacked.time.dt.days_in_month

# Update attributes
monthly_tp_basin_avg.attrs["units"] = "mm"
monthly_tp_basin_avg.attrs["long_name"] = "Basin-Average Monthly Precipitation" 
# Fixed a problem:  This attribute contained a tuple of strings natively. 
# SciPy's NetCDF writer cannot serialize it in this form, producing the KeyError: ('U', 56).
monthly_tp_basin_avg.attrs["GRIB_stepType"] = "multiple steps"
basin_names = ["CE", "CW", "NE", "NO", "NW", "SE", "SW"]
monthly_tp_basin_avg = monthly_tp_basin_avg.assign_coords(basin=basin_names)
monthly_tp_basin_avg.name = "monthly_precipitation"

# Write out a netcdf file to disk.
monthly_tp_basin_avg.to_netcdf(output_path)

# ------------------------------------------------------------------
# Exract carra2 cell data for co-located aws observation sites.
# ------------------------------------------------------------------

