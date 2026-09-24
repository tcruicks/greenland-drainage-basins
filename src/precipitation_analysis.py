# Script opens and reads a netcdf file that contains the basin average monthly precipitation for each of the seven basins.
# Time-series are plotted along with an inset map of the Greenland Ice Sheet drainage basins for viewers reference.

import os
import pathlib
import matplotlib
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd

home_data_dir = os.path.join(
    pathlib.Path.home(),
    'earth-analytics',
    'greenland-temperature',
    'data',
)

# Initialize an array containing basin IDs so we can iterate through them later.
basin_ids = ["CE", "CW", "NE", "NO", "NW", "SE", "SW"]
# Initialize dataframeto hold top 10 precip months for each basin.
precip_table_df = pd.DataFrame()

# Open netcdf file contatining the basin average monthly precipitation for each of the seven basins.
netcdf_path = f"{home_data_dir}/carra2/carra2_monthly_basin_precip.nc"
monthly_tp_basin_avg_da = xr.open_dataarray(netcdf_path)

# STEP 1: Get top 10 values in each basin and stick them in a dataframe.
# The data frame is composed of strings (date (precip)) which works for 
# a printed formatted table.
for basin in basin_ids:

    top_10 = monthly_tp_basin_avg_da.sel(basin=basin).to_pandas().nlargest(10)

    precip_table_df[basin] = [
        f"{date:%b %Y} ({value:.1f} mm)"
        for date, value in zip(top_10.index, top_10.values)
    ]

# STEP 2:  Plot a timer-series of each basins precip.
fig1, ax1 = plt.subplots(figsize=(20, 8))

ax1.plot(monthly_tp_basin_avg_da.time, monthly_tp_basin_avg_da.sel(basin='CE'), label="Basin CE")
ax1.plot(monthly_tp_basin_avg_da.time, monthly_tp_basin_avg_da.sel(basin='CW'), label="Basin CW")
ax1.plot(monthly_tp_basin_avg_da.time, monthly_tp_basin_avg_da.sel(basin='NE'), label="Basin NE")
ax1.plot(monthly_tp_basin_avg_da.time, monthly_tp_basin_avg_da.sel(basin='NO'), label="Basin NO")
ax1.plot(monthly_tp_basin_avg_da.time, monthly_tp_basin_avg_da.sel(basin='NW'), label="Basin NW")
ax1.plot(monthly_tp_basin_avg_da.time, monthly_tp_basin_avg_da.sel(basin='SE'), label="Basin SE")
ax1.plot(monthly_tp_basin_avg_da.time, monthly_tp_basin_avg_da.sel(basin='SW'), label="Basin SW")

# STEP 3: Add an inset map of the Greenland Ice Sheet drainage basins for viewers reference.
# Define the bounds for the inset axes
# [x_start, y_start, width, height] as fractions of the parent axes (0 to 1)
inset_map = f"{home_data_dir}/basins/greenland_basins_inset.png"
inset_map_image = plt.imread(inset_map)

inset_bounds = [0.05, 0.55, 0.12, 0.4]
axins = ax1.inset_axes(inset_bounds)
axins.set_aspect("auto")

axins.imshow(inset_map_image)
# Hide ticks but retain the border
axins.set_xticks([])
axins.set_yticks([])

plt.title("Greenland Ice Sheet Drainage Basin Average Monthly Precipitation", fontsize=14, fontweight='bold', color='blue', loc='center')
plt.legend()

# STEP 4:  Print a table of the top 10 precip months for each basin.
fig2, ax2 = plt.subplots(figsize=(16, 6))

ax2.axis("off")

table = ax2.table(
    cellText=precip_table_df.values,
    colLabels=precip_table_df.columns,
    loc="center"
)

table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1.2, 1.5)

plt.show()

