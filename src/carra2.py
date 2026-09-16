# This script is used to extract single level data from the New generation pan-Arctic regional reanalysis: CARRA2 from 
# ECMWY/Copernicus.  2m surface temperature and surface runoff is extracted.  The downloaded data file contains monthly
# aggregaTED data.
# To work with grib files cfgrib needs to be installed and then specified in xarray commands as the "engine".

import os
import pathlib
import matplotlib.pyplot as plt
import pyproj
import regionmask
import data_utils

home_dir = os.path.join(
    pathlib.Path.home(),
    'earth-analytics',
    'greenland-temperature',
)

carra2_path = os.path.join(
    home_dir,
    'data',
    'cara2',
    'cara2_greenland_monthly_t2m_1985_2025.grib',
)

basins_path = os.path.join(
    home_dir,
    'data',
    'doi_10_7280_D1WT11__v20190329',
    'Greenland_Basins_PS_v1.4.2.shp',
)

# print(home_dir, cara2_path)

# Open the GRIB dataset using my open_cara2 function.
# This failied initially and wanted the package 'pooch' installed.
carra2_ds = data_utils.open_carra2(carra2_path)

# Now open the basins shapefile.
# Will use this to get projectins consistent.
# Will put the shape file into carra2 coordinates.
seven_basins = data_utils.open_basins(basins_path)

# What years are in the dataset?
# start_time = ds.time.min().values
# end_time = ds.time.max().values
# print(f"Start: {start_time}")
# print(f"End:   {end_time}")
# Start: 1985-10-01T00:00:00.000000000
# End:   2025-12-01T00:00:00.000000000

# View all variable names (headers)
# print(ds.dims)
# print(ds["x"])
# print(ds["y"])

# Extract lat/lon for a particular grid cell in the grib file.
# The GRIB file uses the polar stereographic polar map projection so the
# latitude and longitude variables will be 2D arrays indexed by y and x.

# Define your target grid cell indices
y_index = 1000
x_index = 1000

# Retrieve lat/lon using .isel()
lat = carra2_ds.latitude.isel(y=y_index, x=x_index).values
lon = carra2_ds.longitude.isel(y=y_index, x=x_index).values
t2m = carra2_ds["t2m"].isel(y=y_index, x=x_index, time=250).values

# print(f"Temp 2m: {t2m}")
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
# grid spacing:     2500 m × 2500 m

carra2_geographic_crs = pyproj.CRS.from_user_input(
    "+proj=longlat +R=6371229")

# Create a new geodataframe in a new set of coordinates (Carra2 coords).
seven_basin_carra2 = seven_basins.to_crs(carra2_geographic_crs)

# Now make longitude coords consistent.
# Carra2 uses 0-360.  Basins uses -180-+180
carra2_lon_180 = ((carra2_ds.longitude + 180) % 360) - 180
# carra2_ds = carra2_ds.assign_coords(
#     longitude=((carra2_ds) % 360) - 180
# )

new_longitude = carra2_lon_180.isel(y=y_index, x=x_index).values
orig_longitude = carra2_ds.longitude.isel(y=y_index, x=x_index).values
orig_latitude = carra2_ds.latitude.isel(y=y_index, x=x_index).values

# print(new_longitude)
# print(orig_longitude)
# print(orig_latitude)

# seven_basin_carra2 has a index structure.
# We want to be able to reference a column called SUBREGION1
# to refer to the seven basins.
# First Revert the MultiIndex levels back into standard columns
seven_basin_carra2_flat = seven_basin_carra2.reset_index()
# print(seven_basin_carra2_flat.loc[seven_basin_carra2_flat['SUBREGION1'] == 'CE'])

##########################
# Work on making the mask.
##########################

# Create a regionmask object from the GeoDataFrame
# 'names' defines the column used to label the regions
basin_regions = regionmask.from_geopandas(seven_basin_carra2_flat, names="SUBREGION1")

# Create the mask matching carra2_ds coordinates
# lon is the da we created above with longitude expressed -180-+180.
# print(carra2_ds.coords)
mask = basin_regions.mask(carra2_lon_180, carra2_ds.latitude)
print(mask.min().values)
print(mask.max().values)
mask.plot()
plt.show()
# print(seven_basin_carra2.crs)
# print(seven_basin_carra2.total_bounds)

# Use pyproj.Transformer to transform that first grid point
# from geographic coordinates into our new carra2_crs.
# transformer = pyproj.Transformer.from_crs("EPSG:3413", carra2_crs_1, always_xy=True)

# Transform coordinates (longitude, latitude)
# x, y = transformer.transform(-71.616846, 42.113802)
# print(x, y)
