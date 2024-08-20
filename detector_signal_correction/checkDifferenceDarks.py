import os
import sys
import glob
import h5py as h5
from collections import defaultdict
import re
import numpy as np

mgMode = '/gpfs/exfel/u/scratch/SPB/202002/p002442/cheetah/calib/agipd/r0099-r0095-r0101'
gains3Mode = '/gpfs/exfel/u/scratch/SPB/202002/p002442/cheetah/calib/agipd/r0099-r0100-r0101'

mg = glob.glob(os.path.join(mgMode,"*.h5"))
gains3 = glob.glob(os.path.join(gains3Mode,"*.h5"))
panels = [str(i) for i in range(0,16)]
cellIds = [str(i) for i in range(0,352)]


mg_per_panel = {str(int(re.search(r"[\d]+",re.search(r"AGIPD[\d]+[-]+",i).group()).group())): i for i in mg}
gains3_per_panel = {str(int(re.search(r"[\d]+",re.search(r"AGIPD[\d]+[-]+",i).group()).group())): i for i in gains3}



pathData = '/AnalogOffset'

path_to = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/compare'

statistics = {panel: {cellId: 0 for cellId in cellIds} for panel in panels}
result_for_each_panel = {panel: {cellId: np.zeros((512, 128)) for cellId in cellIds} for panel in panels}

for panel in panels:
    mg_file = mg_per_panel[panel]
    gains3_file = gains3_per_panel[panel]
    
    mg_data = h5.File(mg_file, 'r')[pathData]
    gains3_data = h5.File(gains3_file, 'r')[pathData]
    
    for cellId in cellIds:
        result_for_each_panel[panel][cellId] = gains3_data[1,int(cellId),] - mg_data[1,int(cellId),]
        statistics[panel][cellId] += 1


dataHdf5 = '/data/data'


for panel in panels:
    file_name = os.path.join(path_to, "Cheetah-AGIPD{}-compare.h5".format(panel if len(str(panel)) > 1 else ('0' + str(panel))))
    f = h5.File(file_name, 'a')
    
    init_shape = (1,512,128)
    max_shape = (352,512,128)
    
    new_data = f.create_dataset(dataHdf5, init_shape, maxshape=max_shape, dtype=np.float32, chunks=init_shape, compression="gzip", compression_opts=4)

    for cellId in cellIds:
        
        new_data.resize((int(cellId)+1,) + shape_data)
        new_data[int(cellId),] = result_for_each_panel[panel][cellId]/statistics[panel][cellId]

