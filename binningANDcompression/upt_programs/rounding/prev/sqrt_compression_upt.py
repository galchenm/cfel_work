import os
import sys
import numpy as np
import h5py as h5


def round_precision(n,precision):
   return ((n+precision//2)//precision)*precision

def closest_power2(x):
    """
    Return the closest power of 2 by checking whether 
    the second binary number is a 1.
    """
    op = np.floor if len(bin(x)) >= 4 and bin(x)[3] != "1" else np.ceil
    return 2**(op(np.log2(x)))

def shift_bit_length(x):
    return 1<<len(np.binary_repr(x-1))

def round_sqrt(I):
   binary_repr_vec = np.vectorize(closest_power2) #np.vectorize(shift_bit_length)
   koef = 10
   offset = 64
   #q = np.where(I==0,0,np.floor(np.log2(koef*np.sqrt(np.abs(I)))))
   precision = binary_repr_vec(koef*np.sqrt(np.abs(I)).astype(np.int)) #2 ** q
   return np.sign(I)*round_precision(np.abs(I), precision)

def power2(I, N):
    binary_repr_vec = np.vectorize(bin)
    binary_len = np.vectorize(len)
    Ib = binary_repr_vec(I)
    f_neg = lambda x : 1 if '-' == x[0] else 0
    bin_f_neg = np.vectorize(f_neg)
    k = bin_f_neg(Ib)
    len_Ib = binary_len(Ib)
    f = lambda x,k: int(x[3+k]) if len(x)>=4+k else 0
    k_flat = k.ravel()
    Ib_3plk = np.array(list(map(f, Ib.ravel(), k_flat))).reshape(Ib.shape)
    I = np.where( (I == 0) | (len_Ib < N+k) | ((len_Ib == N + k) & (Ib_3plk == 0)), 0, (((-1) ** k) * (2 ** (len_Ib - 3 - k + Ib_3plk))))
    return I

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
    #tmpI = np.where( (len_Ib < 8+k) | ((len_Ib == 8+k) & (Ib_3plk == 0)), 0, ((-1) ** k) * ((2. ** (len_Ib - 3 - k)) * Ib_2plk + (2. ** (len_Ib - 4 - k)) * Ib_3plk + (2. ** (len_Ib - 5 - k + Ib_5plk)) * (np.bitwise_or(Ib_4plk, Ib_5plk))))
    tmpI = np.where( (I == 0) | (len_Ib < N+k) , 0, ((-1) ** k) * ((2. ** (len_Ib - 3 - k)) * Ib_2plk + (2. ** (len_Ib - 4 - k)) * Ib_3plk + (2. ** (len_Ib - 5 - k )) * Ib_4plk) + (2. ** (len_Ib - 5 - k)) * Ib_5plk)
    I = tmpI.astype(np.int32)
    return I

file_cxi = sys.argv[1]
path_to_data_cxi = sys.argv[2]
path_to_data = sys.argv[3]
N = int(sys.argv[4]) + 2 


with h5.File(file_cxi, 'a') as f:
    data = f[path_to_data_cxi]
    shape_data = data.shape[1:]
    num = data.shape[0]
    initShape = (1,) + shape_data
    maxShape = (num,) + shape_data
    d = f.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, compression="gzip", compression_opts=6, shuffle=True)
    
    d[0,] = power2_upt(data[0,], N).astype(np.int32) #(round_sqrt(data[0,].astype(np.int32)))
    
    for i in range(num):
        d.resize((i+1,) + shape_data)
        d[i,] = power2_upt(data[i,], N).astype(np.int32) #(round_sqrt(data[i,].astype(np.int32)))