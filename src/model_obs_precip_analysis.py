import os
import pathlib
import matplotlib
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import geopandas as gpd
import pandas as pd
import data_utils

home_dir = os.path.join(
    pathlib.Path.home(),
    'earth-analytics',
    'greenland-temperature',
)

home_data_dir = os.path.join(
    pathlib.Path.home(),
    home_dir,
    'data',
)

aws_locations_path = os.path.join(
    home_data_dir,
    'AWS',
    'aws_accumulation_stations_full_gdf.shp',
)

basins_path = os.path.join(
    home_data_dir,
    'basins',
    'clean_inset_gdf.shp',
)

carra2_pcp_path = os.path.join(
    home_dir,
    'data',
    'carra2',
    'cara2_greenland_monthly_totprecip_1985_2025.grib',
)

# --------------------------------------------------------------
# --------------------------------------------------------------
# Grab an observation site from each basin's polygon.
# Compare observations to the grid cell co-located with the observation site.
# Make some plots.
# --------------------------------------------------------------
# --------------------------------------------------------------

# STEP 1:  Do a spatial join on geodataframes containing the observation sites 
# and the basin polygons to determine which basin each observation site is located in.

# Load your spatial layers
aws_points = gpd.read_file(aws_locations_path)
basin_polygons = gpd.read_file(basins_path)

# Ensure CRS match
if aws_points.crs != basin_polygons.crs:
    aws_points = aws_points.to_crs(basin_polygons.crs)

# Join points to polygons
# The resulting GeoDataFrame will retain the Point geometry
aws_points_within_basin_polygons = gpd.sjoin(
    left_df=aws_points, 
    right_df=basin_polygons, 
    how="left", 
    predicate="within"
)

# These are the sites we want to focus on.
# They have pre-2000 records.
analysis_sites = ["CEN", "NAU", "CP1", "DY2", "SDL", "HUM", "NAE", "NSE"]

cp1 = aws_points_within_basin_polygons[
    aws_points_within_basin_polygons["Site ID"] == "CP1"
]
# print(cp1[["Site ID", "lat", "lon", "alt","SUBREGION1"]])


# STEP 2: Open the Carra2 dataset

# # Meteorological variable we want to process.
var_name = 'tp'

# Open the GRIB dataset using my open_cara2 function.
carra2_ds = data_utils.open_carra2(carra2_pcp_path)
carra2_ds = carra2_ds.assign_coords(
    longitude=(
        ("y", "x"),
        ((carra2_ds.longitude + 180) % 360 - 180).values
    )
)

# STEP 2: Use Latitude-corrected planar distance to compute nearest 
# neighbor grid cell to each observation site.  

distance_da = (
    (carra2_ds.latitude - cp1['lat'].iloc[0]) ** 2
    + ((carra2_ds.longitude - cp1['lon'].iloc[0])
       * np.cos(np.deg2rad(cp1['lat'].iloc[0]))) ** 2
)

min_index = np.argmin(distance_da.values)
new = np.unravel_index(min_index, distance_da.shape)
print(carra2_ds.latitude.isel(y=new[0], x=new[1]))
print(carra2_ds.longitude.isel(y=new[0], x=new[1]))