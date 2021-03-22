from glob import glob
import proplot as plot
from satpy import Scene
import cartopy.crs as ccrs
from shapely.geometry.polygon import LinearRing

# load scene
filenames = glob('../data/TROPOMI/S5P_NRTI_L2__SO2____20210321T1311*')
scn = Scene(filenames, reader='tropomi_l2')

# load variables
scn.load(['sulfurdioxide_total_vertical_column_1km', 'assembled_lat_bounds', 'assembled_lon_bounds'])

# get variable values
lon = scn['assembled_lon_bounds']
lat = scn['assembled_lat_bounds']

vcd_PBL = scn['sulfurdioxide_total_vertical_column_1km']
vcd_PBL *= vcd_PBL.attrs['multiplication_factor_to_convert_to_DU']
vcd_PBL.attrs['units'] = 'DU'

# plot
fig, axs = plot.subplots(proj='merc')
m = axs.pcolormesh(lon, lat, vcd_PBL,
                   vmin=0.5, vmax=5.5,
                   cmap='Boreal', levels=256)
axs.colorbar(m, loc='r', ticks=0.5, shrink=0.93, label='SO$_2$ column (DU)')


lons = [-22.5, -21.5, -20.5, -21.5]
lats = [64, 65.49, 65.49, 64]
ring = LinearRing(list(zip(lons, lats)))
axs.add_geometries([ring], ccrs.PlateCarree(), facecolor='none', edgecolor='red')

axs.format(lonlim=(-24, -19),
           latlim=(63.5, 65.5),
           lonlabels=True,
           latlabels=True,
           dms=False,
           lonlines=1,
           latlines=1,
           title=vcd_PBL.start_time.strftime('%Y-%m-%d %H:%M (TROPOMI)')
          )

axs.coastlines(resolution='50m')
fig.savefig('../imgs/s5p_fagradalsfjall_so2.jpg')