import os
import geopandas as gpd
import matplotlib.pyplot as plt
import pathlib

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

# Read the basins shapefile into a geopandas dataframe.
gdf = gpd.read_file(basins_path)
#gdf.plot()
#plt.show()

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
seven_basin = gdf.dissolve(by="SUBREGION1")
seven_basin.plot()
plt.show()