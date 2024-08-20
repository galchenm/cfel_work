import os
import sys
import numpy as np
import h5py as h5
import hdf5plugin

def power2_upt(I, N):
    binary_repr_vec = np.vectorize(bin)
    binary_len = np.vectorize(len)
    Ib = binary_repr_vec(I)
    f_neg = lambda x : 1 if '-' == x[0] else 0
    bin_f_neg = np.vectorize(f_neg)
    k = bin_f_neg(Ib)
    len_Ib = binary_len(Ib)
    k_flat = k.ravel()
    f2k = lambda x,k: int(x[2+k]) if len(x)>=3+k else 0
    Ib_2plk = np.array(list(map(f2k, Ib.ravel(), k_flat))).reshape(Ib.shape)
    f3k = lambda x,k: int(x[3+k]) if len(x)>=4+k else 0
    Ib_3plk = np.array(list(map(f3k, Ib.ravel(), k_flat))).reshape(Ib.shape)
    f4k = lambda x,k: int(x[4+k]) if len(x)>=5+k else 0
    Ib_4plk = np.array(list(map(f4k, Ib.ravel(), k_flat))).reshape(Ib.shape)
    f5k = lambda x,k: int(x[5+k]) if len(x)>=6+k else 0
    Ib_5plk = np.array(list(map(f5k, Ib.ravel(), k_flat))).reshape(Ib.shape)
    #tmpI = np.where((I == 0) | (len_Ib < N+k) | ((len_Ib == N + k) &  (Ib_3plk == 0)) , 0, np.where(((len_Ib == N + k) &  (Ib_2plk == 1)), ((-1) ** k) * 2**(N-2), ((-1) ** k) * ((2. ** (len_Ib - 3 - k)) * Ib_2plk + (2. ** (len_Ib - 4 - k)) * Ib_3plk + (2. ** (len_Ib - 5 - k )) * Ib_4plk + (2. ** (len_Ib - 5 - k)) * Ib_5plk)))
    tmpI = np.where((I == 0) | (len_Ib < N+k) , 0, np.where((len_Ib == N + k), ((-1) ** k) * 2**(N-2), ((-1) ** k) * ((2. ** (len_Ib - 3 - k)) * Ib_2plk + (2. ** (len_Ib - 4 - k)) * Ib_3plk + (2. ** (len_Ib - 5 - k )) * Ib_4plk + (2. ** (len_Ib - 5 - k)) * Ib_5plk)))
    I = tmpI.astype(I.dtype)
    return I


N = 9+2
lim_up = 16000
filefrom = '/gpfs/exfel/u/scratch/SPB/202002/p002442/galchenm/processed/blocks/dataReduction/r0043-gv_snr5_dark47/EuXFEL-S00014-r0043-c00.cxi'
h5path  = '/entry_1/instrument_1/detector_1/detector_corrected/data'
f = h5.File(filefrom,'r')
data = f[h5path]
shape_data = data.shape[1:]
num = data.shape[0]
initShape = (1,) + shape_data
maxShape = (num,) + shape_data


path_to_data = '/data/data'
f16int = h5.File('/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/some_files/16int.h5', 'w') # with shuffle
f16intWOneg = h5.File('/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/some_files/16intWOneg.h5', 'w') # with shuffle
f512int16k_32int_with = h5.File('/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/some_files/512int16k_32int_with.h5', 'w')
f512int16k_32int_wo = h5.File('/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/some_files/512int16k_32int_wo.h5', 'w')
f512int16k_16int_with = h5.File('/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/some_files/512int16k_16int_with.h5', 'w')


d16int = f16int.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int16, chunks=initShape, compression="gzip", compression_opts=6, shuffle=True)
d16intWOneg = f16intWOneg.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int16, chunks=initShape, compression="gzip", compression_opts=6, shuffle=True)
d512int16k_32int_with = f512int16k_32int_with.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, compression="gzip", compression_opts=6, shuffle=True)
d512int16k_32int_wo = f512int16k_32int_wo.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, compression="gzip", compression_opts=6, shuffle=False)
d512int16k_16int_with = f512int16k_16int_with.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int16, chunks=initShape, compression="gzip", compression_opts=6, shuffle=True)

tmp = data[0,] if lim_up is None else np.where(data[0,] < lim_up, data[0,], lim_up)
tmp = power2_upt(tmp, N)
d16int[0,] = tmp.astype(np.int16)
d16intWOneg[0,] = (np.where(tmp < 0, 0, tmp)).astype(np.int16)
d512int16k_32int_with[0,] = tmp.astype(np.int32)
d512int16k_32int_wo[0,] = tmp.astype(np.int32)
d512int16k_16int_with[0,] = tmp.astype(np.int16)

for i in range(num):
    d16int.resize((i+1,) + shape_data)
    d16intWOneg.resize((i+1,) + shape_data)
    d512int16k_32int_with.resize((i+1,) + shape_data)
    d512int16k_32int_wo.resize((i+1,) + shape_data)
    d512int16k_16int_with.resize((i+1,) + shape_data)
    tmp = data[i,] if lim_up is None else np.where(data[i,] < lim_up, data[i,], lim_up)
    tmp = power2_upt(tmp, N)
    d16int[i,] = tmp.astype(np.int16)
    d16intWOneg[i,] = (np.where(tmp < 0, 0, tmp)).astype(np.int16)
    d512int16k_32int_with[i,] = tmp.astype(np.int32)
    d512int16k_32int_wo[i,] = tmp.astype(np.int32)
    d512int16k_16int_with[i,] = tmp.astype(np.int16)
    
    
f16int.close() # = h5.File('/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/some_files/16int.h5', 'w') # with shuffle
f16intWOneg.close() # = h5.File('/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/some_files/16intWOneg.h5', 'w') # with shuffle
f512int16k_32int_with.close() # = h5.File('/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/some_files/512int16k_32int_with.h5', 'w')
f512int16k_32int_wo.close() # = h5.File('/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/some_files/512int16k_32int_wo.h5', 'w')
f512int16k_16int_with.close()
f.close()