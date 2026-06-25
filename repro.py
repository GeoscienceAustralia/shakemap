import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

xmin = 119.883
xmax = 121.783
ymin = -20.533
ymax = -18.733

clon = (xmin + xmax) / 2

# To avoid polygon clipping errors at the boundary, ensure the projection extent is a
# little larger than the map extent, being careful to not go past 90:
max_lat = min(ymax + 0.05, ymax + (90 - ymax) / 2)
min_lat = max(ymin - 0.05, ymin + (-90 - ymin) / 2)

proj = ccrs.Mercator(
    central_longitude=clon,
    max_latitude=max_lat,
    min_latitude=min_lat,
    globe=None,
)
geoproj = ccrs.PlateCarree()
fig = plt.figure()
ax = fig.add_axes([0, 0, 1, 1], projection=proj)
ax.set_extent([xmin, xmax, ymin, ymax], crs=geoproj)
fig.canvas.draw()
oceans = cfeature.NaturalEarthFeature(
    category="physical",
    name="ocean",
    scale="10m",
    facecolor="blue",
)
ax.add_feature(oceans, edgecolor="black")
plt.draw()
plt.show()
