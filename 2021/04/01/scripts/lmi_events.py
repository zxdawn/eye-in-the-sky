import os
os.environ['SATPY_CONFIG_PATH'] = '../../satpy_config/'

import pandas as pd
import xarray as xr
from glob import glob
import proplot as plot
from pyresample.bucket import BucketResampler
from pyresample import create_area_def

# Disable a few warnings:
import warnings
warnings.simplefilter("ignore")


def preproc(ds):
    '''Add the time dimension/coordinate'''
    drop_vars = list(ds.keys())
    for keep_var in keep_vars:
        drop_vars.remove(keep_var)

    ds = ds.drop_vars(drop_vars)
    ds = ds.rename({'x': 'time'}).assign_coords(time=pd.to_datetime(ds.attrs['time_coverage_start'],
                                                                    format='%Y-%m-%dT%H:%M:%S.%fZ')
                                                + pd.to_timedelta(ds['EOT'].values))
    ds = ds.drop_vars(['EOT'])

    return ds


filenames = sorted(glob('../data/lmi/FY4A-_LMI*LMIE_SING_NUL_20210331*'))
keep_vars = ['LON', 'LAT', 'EOT']

# read all data
ds = xr.concat([xr.open_mfdataset(f, parallel=True, preprocess=preproc) for f in filenames],
               dim='time').sortby('time')

# create area for resample
area = create_area_def('main_area',
                       {'proj': 'longlat', 'datum': 'WGS84'},
                       area_extent=[105-0.05, 17-0.05, 125+0.05, 38+0.05],
                       resolution=0.1,
                       units='degrees',
                       description='0.1x0.1 degree lat-lon grid')

lon_coord, lat_coord = area.get_lonlats()

# resample and sum counts
resampler = BucketResampler(area, ds.LON.data, ds.LAT.data)
counts = resampler.get_count()

# plot
fig, axs = plot.subplots(proj='pcarree')
m = axs.pcolormesh(lon_coord, lat_coord, counts,
                   cmap='Thermal',
                   levels=256,
                   vmin=0, vmax=40)

axs.colorbar(m, loc='b', ticks=5, extend='max')
axs.coastlines(color='white', linewidth=0.1)

axs.format(
           lonlim=(lon_coord.min(), lon_coord.max()),
           latlim=(lat_coord.min(), lat_coord.max()),
           grid=False,
           title='FY-4A LMI Events \n (2021-03-31 04:00 ~  19:00 UTC)'
           )

fig.savefig('../imgs/lmi_20210331.jpg')
