import os
import warnings
warnings.filterwarnings("ignore")
os.environ['SATPY_CONFIG_PATH'] = '../../satpy_config/'

from satpy import Scene
from glob import glob
from trollimage.colormap import greys, spectral

# set the corresponding colormap ticks range
greys.set_range(-40, 30)
spectral.set_range(-90, -40)

filenames = list(sorted(glob('../data/agri/FY4A-_AGRI--*NOM_20210331*_4000M_V0001.HDF')))


def load_data(filename):
    scn = Scene(reader="agri_l1", filenames=[filename])
    scn.load(['C12'])
    img = scn.resample('huadong', radius_of_influence=5000, cache_dir='./')

    print(img.attrs['start_time'])
    print(img['C12'].min().values - 273.15)

    return scn, img


def plot_data(img):
    # save dataset to image
    deco = [{'text': {'txt': ''.join(img.attrs['sensor']).upper() + ' '
                             + img.attrs['start_time'].strftime('%Y-%m-%d %H:%M (UTC)'),
                      'font': '/usr/share/fonts/dejavu/DejaVuSerif-Bold.ttf',
                      'font_size': 40, 'height': 10,
                      'bg': 'black', 'bg_opacity': 80, 'line': 'white',
                      'cursor':[510, 0]}}
            ]

    img.save_datasets(base_dir='../imgs/',
                      filename='{sensor}_{name}_{start_time:%Y%m%d_%H%M}.jpg',
                      compute=True,
                      datasets=['C12'],
                      writer='simple_image',
                      overlay={'coast_dir': '/public/home/zhangxin/new/data/shp/',
                               'color': (255, 255, 255), 'width': 1., 'resolution': 'l'},
                      decorate={'decorate': deco},
                      fill_value=0
                      )


for filename in filenames:
    scn, img = load_data(filename)
    plot_data(img)
    del scn
    del img
