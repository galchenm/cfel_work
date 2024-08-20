import h5py
import numpy as np
import time
import scipy.constants

import argparse

import importlib
import sys

from cfelpyutils import cfel_crystfel, cfel_geom
import os
from collections import namedtuple


#geometryFileName = "/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/to_change/streamviewer/src/cfelpyutils/agipd_2450_v9_cheetah.geom"
geometryFileName = "/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/to_change/streamviewer/src/cfelpyutils/agipd_2450_v9_vds_U.geom"
#geometry = crystfel_utils.load_crystfel_geometry(geometryFileName)
pixm = cfel_geom.pixel_maps_from_geometry_file(geometryFileName)

print(pixm.x)
print(geometryFileName)