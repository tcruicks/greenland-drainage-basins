import os
import pathlib
import numpy as np
import rasterio
from affine import Affine
import matplotlib.pyplot as plt
import matplotlib.image as mping
import matplotlib.colors as colors
from rasterio.plot import show
from rasterio.enums import Resampling

home_dir = os.path.join(
    pathlib.Path.home(),
    'earth-analytics',
    'greenland-temperature',
)

dem_path = os.path.join(
    home_dir,
    'data',
    'dem',
    'gimpdem_90m_v01.1.tif',
)

dem_resampled_path = os.path.join(
    home_dir,
    'data',
    'dem',
    'resampled_dem.tiff'
)

# Open the Greenland DEM file but downscale it.
with rasterio.open(dem_path) as src:
    # Downsample by a factor of 10 (reads every 10th pixel)
    # This reduces data size by 100x while keeping the map profile clean
    scale_factor = 10 
    
    out_shape = (
        src.count,
        int(src.height / scale_factor),
        int(src.width / scale_factor)
    )

    # Read data with resampling
    dem_data = src.read(
       out_shape=out_shape,
       resampling=rasterio.enums.Resampling.bilinear
    )

    # 4. Scale the transform matrix so coordinates stay spatially accurate
    # We scale by the inverse of how the pixel counts changed
    transform = src.transform * src.transform.scale(
        (src.width / dem_data.shape[-1]),
        (src.height / dem_data.shape[-2])
    )

    # Copy the original profile and update it with new shape and transform
    profile = src.profile.copy()

profile.update({
    'height': dem_data.shape[-2],
    'width': dem_data.shape[-1],
    'transform': transform
})

# 2. Write the new raster to disk
with rasterio.open(dem_resampled_path, 'w', **profile) as dst:
    dst.write(dem_data, indexes=1 if dem_data.ndim == 2 else None)

# Python's with statement manages the open file for you.
# Open this file, call the resulting object src, let me 
# work with it inside this indented block, and then properly close the file when I'm finished.

# Think of src as the open GeoTIFF plus the information needed to interpret it geographically.
# The code reads like this:  src = rasterio.open(dem_resampled_path)
with rasterio.open(dem_resampled_path) as src:
    resampled_dem = src.read(1) # Give me the pixel values from band 1 in a numpy array.
    bounds = src.bounds # Asking the Rasterio dataset for another piece of information: geographic/projected extent.
    # Read the first band (elevation values)
    elevation = src.read(1)
    # Get the spatial bounding box for correct axis labeling
    extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]


fig, ax = plt.subplots(figsize=(6, 8))

# If you have the cmocean library installed: 
import cmocean
#color_map = cmocean.cm.ice
color_map = 'Blues_r'
  
img = ax.imshow(
    resampled_dem, 
    cmap=color_map, 
    extent=extent,
    )

# Add countour lines to the DEM.
contours = [2000, 2500, 3000, 3500]
# We explicitly tell contour() which geographic coordinate corresponds to each row and column:
x = np.linspace(bounds.left, bounds.right, resampled_dem.shape[1])
y = np.linspace(bounds.top, bounds.bottom, resampled_dem.shape[0])
contour_lines = ax.contour(
    x,
    y,
    resampled_dem, 
    levels=contours,             # Number of contour lines
    colors="black", 
    linewidths=0.4,
    linestyles='dotted'
)
# Add labels to the contour lines
ax.clabel(contour_lines, inline=True, fontsize=10, fmt='%1.0f')

# Add a styling details
cbar = fig.colorbar(img, ax=ax, label="Elevation above ellipsoid (meters)", shrink=0.7)
ax.set_title("Greenland Ice Sheet - GIMP DEM (90m) Resampled to 900m", fontsize=12, fontweight='bold')
ax.set_xlabel("X Coordinate (m)")
ax.set_ylabel("Y Coordinate (m)")

# Keep axes clean or matching the EPSG:3413 Polar Stereographic coordinates
plt.tight_layout()
plt.show()
