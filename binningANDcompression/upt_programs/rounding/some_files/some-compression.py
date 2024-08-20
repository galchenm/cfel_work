import os
import sys
import numpy as np
import h5py as h5
import hdf5plugin



filefrom = '/gpfs/exfel/u/scratch/SPB/202002/p002442/galchenm/processed/blocks/dataReduction/r0043-gv_snr5_dark47/EuXFEL-S00014-r0043-c00.cxi'
h5path  = '/entry_1/instrument_1/detector_1/detector_corrected/data'
f = h5.File(filefrom,'r')
data = f[h5path]
shape_data = data.shape[1:]
num = data.shape[0]
initShape = (1,) + shape_data
maxShape = (num,) + shape_data


path_to_data = '/data/data'
#f_LZF = h5.File('/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/some_files/lzf.h5', 'w')
#f_LZF_with_shuffle = h5.File('/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/some_files/lzf_with_shuffle.h5', 'w')
#f_bloscNOSHUFFLE = h5.File('/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/some_files/lz4hc_NOSHUFFLE_clevel6.h5', 'w')
#f_bloscBYTESHUFFLE = h5.File('/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/some_files/zlib_BYTESHUFFLE.h5', 'w')
#f_bloscBITSHUFFLE = h5.File('/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/some_files/zlib_BITSHUFFLE.h5', 'w')
f_LZ4 = h5.File('/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/some_files/Zfp_lossless.h5', 'w')


#d_LZF = f_LZF.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int16, chunks=initShape, compression="lzf", shuffle=False)
#d_LZF_with_shuffle = f_LZF_with_shuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int16, chunks=initShape, compression="lzf", shuffle=True)
#d_bloscNOSHUFFLE= f_bloscNOSHUFFLE.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='lz4hc', clevel=6, shuffle=hdf5plugin.Blosc.NOSHUFFLE))
#d_bloscBYTESHUFFLE = f_bloscBYTESHUFFLE.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='zlib', clevel=6, shuffle=hdf5plugin.Blosc.SHUFFLE))
#d_bloscBITSHUFFLE = f_bloscBITSHUFFLE.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int16, chunks=initShape, **hdf5plugin.Blosc(cname='zlib', clevel=6, shuffle=hdf5plugin.Blosc.BITSHUFFLE))
d_LZ4 = f_LZ4.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int16, chunks=initShape, **hdf5plugin.Zfp(reversible=True))


#d_LZF[0,] = data[0,]
#d_LZF_with_shuffle[0,] = data[0,]

#d_bloscNOSHUFFLE[0,] = data[0,]
#d_bloscBYTESHUFFLE[0,] = data[0,]
#d_bloscBITSHUFFLE[0,] = data[0,]
d_LZ4[0,] = data[0,]

for i in range(num):
    #d_LZF.resize((i+1,) + shape_data)
    #d_LZF_with_shuffle.resize((i+1,) + shape_data)
    #d_bloscNOSHUFFLE.resize((i+1,) + shape_data)
    #d_bloscBYTESHUFFLE.resize((i+1,) + shape_data)
    #d_bloscBITSHUFFLE.resize((i+1,) + shape_data)
    d_LZ4.resize((i+1,) + shape_data)

    #d_LZF[i,] = data[i,]
    #d_LZF_with_shuffle[i,] = data[i,]
    #d_bloscNOSHUFFLE[i,] = data[i,]
    #d_bloscBYTESHUFFLE[i,] = data[i,]
    #d_bloscBITSHUFFLE[i,] = data[i,]
    d_LZ4[i,] = data[i,]
   
#f_LZF.close()
#f_LZF_with_shuffle.close()
f_LZ4.close()

#f_bloscNOSHUFFLE.close()
#f_bloscBYTESHUFFLE.close()
#f_bloscBITSHUFFLE.close()
f.close()