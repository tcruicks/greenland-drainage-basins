# This script is used to extract single level data from the New generation pan-Arctic regional reanalysis: CARRA2 from
# ECMWY/Copernicus.  2m surface temperature and surface runoff is extracted.  The downloaded data file contains monthly
# aggregaTED data.
# To work with grib files cfgrib needs to be installed and then specified in xarray commands as the "engine".

import os
import pathlib
import matplotlib.pyplot as plt
import pyproj
import regionmask
import pandas as pd
import geopandas as gpd
from sklearn.covariance import log_likelihood
import data_utils

home_dir = os.path.join(
    pathlib.Path.home(),
    'earth-analytics',
    'greenland-temperature',
)

carra2_path = os.path.join(
    home_dir,
    'data',
    'carra2',
    'cara2_greenland_monthly_t2m_1985_2025.grib',
)

basins_path = os.path.join(
    home_dir,
    'data',
    'doi_10_7280_D1WT11__v20190329',
    'Greenland_Basins_PS_v1.4.2.shp',
)

aws_descriptions_path = os.path.join(
    home_dir,
    'data',
    'AWS',
    'essd-18-2829-2026-t03.csv',
)

aws_locations_path = os.path.join(
    home_dir,
    'data',
    'AWS',
    'AWS_latest_locations.csv',
)

aws_locations_output_path = os.path.join(
    home_dir,
    'data',
    'AWS',
    'aws_accumulation_stations_full_gdf.shp',
)

###################
# Now we will open, read, and plot a csv file of AWS station locations
###################

# A master list of descriptions of AWS sites including installation date.
aws_site_descriptions_df = pd.read_csv(aws_descriptions_path)

# Just make a df of AWS located in accumulation zones.
aws_accumulation_stations_df = aws_site_descriptions_df[aws_site_descriptions_df['Site type'] == 'Accumulation']

# Call the open_basins function to read and work with the shapefile.
# aws_locations_pd has 'stid', 'timestamp', 'lat', 'lon' and 'alt'
aws_locations_gdf = data_utils.open_aws_locations(aws_locations_path)

# # Combine aws_accumulation_stations_df with aws_locations_gdf so that we can take
# lat lon from aws_locations_gdf and stick them into aws_accumulation_stations_df.
aws_accumulation_stations_full_df  = pd.merge(
    aws_accumulation_stations_df, 
    aws_locations_gdf[['stid', 'lat', 'lon', 'alt']], 
    left_on='Site ID', 
    right_on='stid', 
    how='left'
)
# Drop unneccessary carry over station ide from aws_locations_gdf.
aws_accumulation_stations_full_df = aws_accumulation_stations_full_df.drop(columns=['stid'])

# Manually inserting the lat/lon/alt for CEN2 into CEN.
# Two methods to do the replace.
aws_accumulation_stations_full_df.iloc[0, 5] = 77.1818989
aws_accumulation_stations_full_df.iloc[0, 6] = -61.1160917
aws_accumulation_stations_full_df.loc[aws_accumulation_stations_full_df['Site ID'] == 'CEN', 'alt'] = 1894.6741

# Convert aws_accumulation_stations_full_df to a GeoDataFrame
aws_accumulation_stations_full_gdf = gpd.GeoDataFrame(
    aws_accumulation_stations_full_df, 
    geometry=gpd.points_from_xy(aws_accumulation_stations_full_df.lon, aws_accumulation_stations_full_df.lat),
    crs="EPSG:4326"
)
aws_accumulation_stations_full_gdf.to_file(aws_locations_output_path)

# Call the open_basins function to read and work with the shapefile.
seven_basin_gdf = data_utils.open_basins(basins_path)
seven_basin_gdf = seven_basin_gdf.to_crs('EPSG:4326')

fig, ax = plt.subplots(figsize=(6, 8))

ax.set_xlim(-75, -10)
ax.set_ylim(58, 85)

seven_basin_gdf.plot(ax=ax)

aws_accumulation_stations_full_gdf.plot(
    ax=ax,
    color='black',
    markersize=25,
)

# Loop through the GeoDataFrame to add ID text beside each point
for idx, row in aws_accumulation_stations_full_gdf.iterrows():
    # row.geometry.x is longitude, row.geometry.y is latitude
    ax.annotate(
        text=row['Site ID'],
        xy=(row.geometry.x, row.geometry.y),
        # Offset text by 5 points to the right and up
        xytext=(5, 5),
        textcoords="offset points",  # Use point-based offset
        fontsize=10,
    )

plt.show()
