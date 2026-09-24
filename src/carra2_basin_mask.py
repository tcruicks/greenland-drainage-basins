# Creates and writes a basins_mask_da dataarray that contains the SUBREGION basins.

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

carra2_pcp_path = os.path.join(
    home_dir,
    'data',
    'cara2',
    'cara2_greenland_monthly_totprecip_1985_2025.grib',
)

mask_path = os.path.join(
    home_dir,
    "data",
    "basin_mask.nc"
)

# Open the GRIB dataset using my open_cara2 function.
# This failied initially and wanted the package 'pooch' installed.
carra2_ds = data_utils.open_carra2(carra2_pcp_path)

# Now open the basins shapefile.
# Will use this to get projectins consistent.
# Will put the shape file into carra2 coordinates.
seven_basins_gdf = data_utils.open_basins(basins_path)

# What years are in the dataset?
start_time = carra2_ds.time.min().values
end_time = carra2_ds.time.max().values
print(f"Start: {start_time}")
print(f"End:   {end_time}")

# Extract lat/lon for a particular grid cell in the grib file.
# The GRIB file uses the polar stereographic polar map projection so the
# latitude and longitude variables will be 2D arrays indexed by y and x.

# Define your target grid cell indices
y_index = 1000
x_index = 1000

# Retrieve lat/lon using .isel()
lat = carra2_ds.latitude.isel(y=y_index, x=x_index).values
lon = carra2_ds.longitude.isel(y=y_index, x=x_index).values

# Get more projection/grid information
# Trying to determine what are the projection parameters/CRS of the CARRA2 2.5-km analysis grid?
# It is polar stereographic and so is the seven_basins (EPSG:3413) but need more detail on carra2.

# Greenland basins
#    EPSG:3413
#    polar stereographic
#    WGS 84 ellipsoid
# 
# CARRA2
# Projection:       North polar stereographic
# Earth:            sphere, radius = 6,371,229 m
# lat_ts (LaD):     90°
# lon_0 (LoV):      330° = -30°
# grid spacing:     2500 m * 2500 m

carra2_geographic_crs = pyproj.CRS.from_user_input(
    "+proj=longlat +R=6371229")

# Create a new geodataframe in a new set of coordinates from Carra2 coords.
seven_basin_carra2_gdf = seven_basins_gdf.to_crs(carra2_geographic_crs)

# Now make longitude coords consistent.
# Carra2 uses 0-360.  Basins uses -180-+180
carra2_lon_180 = ((carra2_ds.longitude + 180) % 360) - 180

new_longitude = carra2_lon_180.isel(y=y_index, x=x_index).values
orig_longitude = carra2_ds.longitude.isel(y=y_index, x=x_index).values
orig_latitude = carra2_ds.latitude.isel(y=y_index, x=x_index).values

# seven_basin_carra2 has a index structure.
# We want to be able to reference a column called SUBREGION1
# to refer to the seven basins.
# First Revert the MultiIndex levels back into standard columns
seven_basin_carra2_flat_gdf = seven_basin_carra2_gdf.reset_index()

##########################
# Work on making the mask.
##########################

# Create a regionmask object from the GeoDataFrame
# 'names' defines the column used to label the regions
basin_regions = regionmask.from_geopandas(seven_basin_carra2_flat_gdf, names="SUBREGION1")

# Create the mask matching carra2_ds coordinates
# lon is the da we created above with longitude expressed -180-+180.
basins_mask_da = basin_regions.mask(carra2_lon_180, carra2_ds.latitude)

# Plot seven_basins_gdf over basins_nmask_da to verify that the coords and projection match up.
# First, we need to get basins_mask_da into the same coords as seven_basins_gdf
basins_mask_da = basins_mask_da.assign_coords(
    longitude=(("y", "x"), ((basins_mask_da.longitude + 180) % 360 - 180).values)
)
# Let's save that masked basins file to a netcdf file so we dont have to re-do 
# that heavy computation again.
basins_mask_da.to_netcdf(mask_path)