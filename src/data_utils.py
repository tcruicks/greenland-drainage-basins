# A script that contains functions that open and load data sets needed for the project.
# 1) Open and load the Greenland ice sheet drainage basins shapefile.
# 2) Open and load the Carra2 dataset grib file that contains 2 meter temperature (monthly average).

import geopandas as gpd
import xarray as xr

def open_basins(basins_path):
    # Function receeves the path to the drainage basin shapefile.
    # Reads the file and then creates the shapefile of the seven basins.

    # Read the basins shapefile into a geopandas dataframe.
    gdf = gpd.read_file(basins_path)
    # Aggregate smaller geometry into the larger basin geometry outlines.
    seven_basins = gdf.dissolve(by="SUBREGION1")

    return seven_basins


def open_carra2(carra2_path):
    # Function opens the carra2 grib file and puts it into a dataset.

    # Open the GRIB dataset.
    # This failied initially and wanted the package 'pooch' installed.
    ds = xr.open_dataset(carra2_path, engine="cfgrib")

    return ds
