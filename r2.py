#!/usr/bin/env python


import cartopy.crs as ccrs  # projections
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

BORDER_ZORDER = 1110

if __name__ == "__main__":
    bounds = (
        -88.76666666666667,
        -86.93333333333334,
        37.73333333333333,
        39.18333333333333,
    )
    figsize = (10.0, 9.947416426343834)
    xmin, xmax, ymin, ymax = bounds
    clon = (xmin + xmax) / 2
    if xmax < 0 and xmax < xmin:
        clon = (xmin + (xmax + 360)) / 2

    clat = (ymin + ymax) / 2
    proj = ccrs.Mercator(
        central_longitude=clon, min_latitude=ymin, max_latitude=ymax, globe=None
    )
    geoproj = ccrs.PlateCarree()
    figure = plt.figure(figsize=figsize)

    aspect = 0.9941078696774519

    # Note: dimensions are: [left, bottom, width, height]
    dim_left = 0.1
    dim_bottom = 0.19
    dim_width = 0.8
    dim_height = dim_width / aspect

    dimensions = [dim_left, dim_bottom, dim_width, dim_height]

    ax = figure.add_axes(dimensions, projection=proj)
    ax.set_extent([xmin, xmax, ymin, ymax], crs=geoproj)
    states_provinces = cfeature.NaturalEarthFeature(
        category="cultural",
        name="admin_1_states_provinces_lines",
        scale="10m",
        facecolor="none",
    )

    ax.add_feature(states_provinces, edgecolor="black", zorder=BORDER_ZORDER)
    plt.draw()
    plt.show()
