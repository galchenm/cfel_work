import os
import sys
import numpy as np
import h5py as h5


file_cxi = sys.argv[1] #
N = 4096
path_to_data_cxi = "/entry_1/instrument_1/detector_1/data" #"/entry_1/instrument_1/detector_1/data"

path_to_data = "/entry_1/instrument_1/detector_1/data_4096int" #"/entry_1/instrument_1/detector_1/dataNewShuffle" #"/entry_1/instrument_1/detector_1/dataNewShuffle"
path_to_dataFloat = "/entry_1/instrument_1/detector_1/dataFloat"
path_to_dataSixT = "/entry_1/instrument_1/detector_1/data_16new"
path_to_data1024= "/entry_1/instrument_1/detector_1/dataOneZeroTwoFourNEW"
path_to_databyte= "/entry_1/instrument_1/detector_1/dataB_BytewoSHUFFLE"



with h5.File(file_cxi, 'a') as f:
    data = f[path_to_data_cxi]
    shape_data = data.shape[1:]
    num = data.shape[0]
    initShape = (1,) + shape_data
    maxShape = (num,) + shape_data
    d = f.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32,chunks=initShape, compression="gzip", compression_opts=6,shuffle=True)
    
    dSixT = f.create_dataset(path_to_dataSixT, initShape, maxshape=maxShape, dtype=np.int32,chunks=initShape, compression="gzip", compression_opts=6,shuffle=True)
    dFloat = f.create_dataset(path_to_dataFloat, initShape, maxshape=maxShape, dtype=np.float32,chunks=initShape, compression="gzip", compression_opts=6)
    d1024 = f.create_dataset(path_to_data1024, initShape, maxshape=maxShape, dtype=np.int32,chunks=initShape, compression="gzip", compression_opts=6,shuffle=True)
    dbyte = f.create_dataset(path_to_databyte, initShape, maxshape=maxShape, dtype=np.byte,chunks=initShape, compression="gzip", compression_opts=6,shuffle=True)
    
    dFloat[0,] = data[0,].astype(np.float32) + np.random.rand(shape_data[0],shape_data[1]) #data[0,].astype(np.int32) #np.round(data[0,], 0).astype(np.int32)
    dSixT[0,] = (np.round(data[0,]/16,0)*16).astype(np.int32) #np.round(data[0,], 0).astype(np.int32)
    d[0,] = (np.round(data[0,]/N,0)*N).astype(np.int32) #data[0,].astype(np.int32)
    d1024[0,] = (np.round(data[0,]/1024,0)*1024).astype(np.int32)
    dbyte[0,] = (np.round(data[0,]/1024,0)).astype(np.byte)
    
    for i in range(num):
        dFloat.resize((i+1,) + shape_data)
        dSixT.resize((i+1,) + shape_data)
        d.resize((i+1,) + shape_data)
        d1024.resize((i+1,) + shape_data)
        dbyte.resize((i+1,) + shape_data)
        dFloat[i,] = data[i,].astype(np.float32) + np.random.rand(shape_data[0],shape_data[1]) #data[i,].astype(np.int32) #np.round(data[i,], 0).astype(np.int32)
        dSixT[i,] = (np.round(data[i,]/16,0)*16).astype(np.int32)
        d[i,] = (np.round(data[i,]/N,0)*N).astype(np.int32)
        d1024[i,] = (np.round(data[i,]/1024,0)*1024).astype(np.int32)
        dbyte[i,] = (np.round(data[i,]/1024,0)).astype(np.byte)