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
basins_gdf = data_utils.open_basins(basins_path)

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
seven_basin_gdf = basins_gdf.dissolve(by="SUBREGION1")

#-------------------------------------
'''
# How many little polygons are in each basin?
for basin_id, row in seven_basin_gdf.iterrows():
    geom = row.geometry

    if geom.geom_type == "MultiPolygon":
        print(basin_id, len(geom.geoms))
    else:
        print(basin_id, 1)
'''

# We want to plot only the largest basin geometery not all the smaller ones.
# Find the max size polygon only and plot that.
from shapely.geometry import Polygon

inset_basins_gdf = seven_basin_gdf.copy()

inset_basins_gdf["geometry"] = inset_basins_gdf.geometry.apply(
    lambda geom: max(geom.geoms, key=lambda polygon: polygon.area)
)

clean_inset_gdf = inset_basins_gdf.copy()

clean_inset_gdf["geometry"] = clean_inset_gdf.geometry.apply(
    lambda geom: Polygon(geom.exterior)
)
# Write this gdf to a file.
# It represents the basins in as clean polyugons as possible.
clean_inset_gdf.to_file("../data/basins/clean_inset_gdf.shp")
 #-------------------------------------
 
'''
fig, ax = plt.subplots(figsize=(4, 6))

clean_inset_gdf.plot(ax=ax, color="white", edgecolor="black")

for basin_id, row in seven_basin_gdf.iterrows():

    point = row.geometry.representative_point() # This is an auto label placement method.

    ax.annotate(
        text=basin_id,
        xy=(point.x, point.y),
        ha="center",
        fontsize=12,
    )

# Dont want tick labels for the inset map.
ax.set_axis_off()
# Remove margins around the axes
fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

plt.savefig(
    "../data/basins/greenland_basins_inset.png",
    dpi=300,
    bbox_inches="tight",
    transparent=True,
    pad_inches=0,
)

# Try transforming seven_basins into geographic coordinates from the carra2 grib file.
# gpd_transformed = gpd.to_crs(EPSG:4326)

'''