# This script loads a geodataframe with greenland ice sheet drainage basin shapefile.
# There are seven main drainage basins and we use the Greenland_Basins_PS_v1.4.2.shp file.
# The script relies on a local copy of the shapefile filder.

import os
import matplotlib.pyplot as plt
import pathlib
import data_utils

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

# Call the open_basins function to read and work with the shapefile.
seven_basin = data_utils.open_basins(basins_path)

# gdf.plot()
# plt.show()

# Just print the columns names
# print(list(gdf.columns))
# Only print unique basin names
# print(gdf['SUBREGION1'].unique())

# Select and plot only one basin and associated geometry
# filtered_gdf = gdf[gdf["SUBREGION1"] == "NW"]
# filtered_gdf.plot()
# plt.show()
# Print out all the rows for NW basin
# print(gdf[gdf["SUBREGION1"] == "NW"])

# Aggregate smaller geometry into the larger basin geometry outlines.
# seven_basin = gdf.dissolve(by="SUBREGION1")
# seven_basin.plot()
# plt.show()

# Try transforming seven_basins into geographic coordinates from the carra2 grib file.
# gpd_transformed = gpd.to_crs(EPSG:4326)

print(seven_basin.crs)
print(seven_basin.shape)