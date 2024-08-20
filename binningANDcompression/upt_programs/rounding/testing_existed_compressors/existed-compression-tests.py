#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import numpy as np
import h5py as h5
import hdf5plugin

import tables



filefrom = sys.argv[1] #'/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/some_files/512int16k_32int_wo.h5'
h5path  = sys.argv[2] #'/data/data'
f = h5.File(filefrom,'r')
data = f[h5path]

shape_data = data.shape[1:]
num = data.shape[0]
initShape = (1,) + shape_data
maxShape = (num,) + shape_data



##########  "BitShuffle can only be used inside Blosc")
with tables.open_file(
    filefrom.split('.')[0]+'_bzip2_level6_wo_shuffle.h5',
    mode="w",
    filters=tables.Filters(
        complib="bzip2",
        complevel=6,
        shuffle=False,
        bitshuffle=False,
        fletcher32=False,
    ),
) as hdf:
    # the output file has this default structure
    group1 = hdf.create_group("/", "data", "")
    hdf.create_carray("/data", "data", obj=dataset, chunkshape=initShape)


with tables.open_file(
    filefrom.split('.')[0]+'_bzip2_level6_with_shuffle.h5',
    mode="w",
    filters=tables.Filters(
        complib="bzip2",
        complevel=6,
        shuffle=True,
        bitshuffle=False,
        fletcher32=False,
    ),
) as hdf:
    # the output file has this default structure
    group1 = hdf.create_group("/", "data", "")
    hdf.create_carray("/data", "data", obj=dataset, chunkshape=initShape)


##########
with tables.open_file(
    filefrom.split('.')[0]+'_bzip2_level9_wo_shuffle.h5',
    mode="w",
    filters=tables.Filters(
        complib="bzip2",
        complevel=9,
        shuffle=False,
        bitshuffle=False,
        fletcher32=False,
    ),
) as hdf:
    # the output file has this default structure
    group1 = hdf.create_group("/", "data", "")
    hdf.create_carray("/data", "data", obj=dataset, chunkshape=initShape)


with tables.open_file(
    filefrom.split('.')[0]+'_bzip2_level9_with_shuffle.h5',
    mode="w",
    filters=tables.Filters(
        complib="bzip2",
        complevel=9,
        shuffle=True,
        bitshuffle=False,
        fletcher32=False,
    ),
) as hdf:
    # the output file has this default structure
    group1 = hdf.create_group("/", "data", "")
    hdf.create_carray("/data", "data", obj=dataset, chunkshape=initShape)


f_gzip_level6_wo = h5.File(filefrom.split('.')[0]+'_gzip_level_6_wo_shuffle.h5','w')
f_gzip_level6_with = h5.File(filefrom.split('.')[0]+'_gzip_level_6_with_shuffle.h5','w')
f_gzip_level9_wo = h5.File(filefrom.split('.')[0]+'_gzip_level_9_wo_shuffle.h5','w')
f_gzip_level9_with = h5.File(filefrom.split('.')[0]+'_gzip_level_9_with_shuffle.h5','w')


f_lzf_wo = h5.File(filefrom.split('.')[0]+'_lzf_wo_shuffle.h5','w')
f_lzf_with = h5.File(filefrom.split('.')[0]+'_lzf_with_shuffle.h5','w')


########
f_Blosc_lz4_level_6_noshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_lz4_level_6_wo_shuffle.h5','w')
f_Blosc_lz4_level_6_byteshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_lz4_level_6_with_shuffle.h5','w')
f_Blosc_lz4_level_6_bitshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_lz4_level_6_with_bitshuffle.h5','w')

f_Blosc_lz4_level_9_noshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_lz4_level_9_wo_shuffle.h5','w')
f_Blosc_lz4_level_9_byteshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_lz4_level_9_with_shuffle.h5','w')
f_Blosc_lz4_level_9_bitshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_lz4_level_9_with_bitshuffle.h5','w')



#####
f_Blosc_lz4hc_level_6_noshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_lz4hc_level_6_wo_shuffle.h5','w')
f_Blosc_lz4hc_level_6_byteshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_lz4hc_level_6_with_shuffle.h5','w')
f_Blosc_lz4hc_level_6_bitshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_lz4hc_level_6_with_bitshuffle.h5','w')

f_Blosc_lz4hc_level_9_noshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_lz4hc_level_9_wo_shuffle.h5','w')
f_Blosc_lz4hc_level_9_byteshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_lz4hc_level_9_with_shuffle.h5','w')
f_Blosc_lz4hc_level_9_bitshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_lz4hc_level_9_with_bitshuffle.h5','w')

#####
f_Blosc_blosclz_level_6_noshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_blosclz_level_6_wo_shuffle.h5','w')
f_Blosc_blosclz_level_6_byteshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_blosclz_level_6_with_shuffle.h5','w')
f_Blosc_blosclz_level_6_bitshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_blosclz_level_6_with_bitshuffle.h5','w')

f_Blosc_blosclz_level_9_noshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_blosclz_level_9_wo_shuffle.h5','w')
f_Blosc_blosclz_level_9_byteshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_blosclz_level_9_with_shuffle.h5','w')
f_Blosc_blosclz_level_9_bitshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_blosclz_level_9_with_bitshuffle.h5','w')

########
f_Blosc_snappy_level_6_noshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_snappy_level_6_wo_shuffle.h5','w')
f_Blosc_snappy_level_6_byteshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_snappy_level_6_with_shuffle.h5','w')
f_Blosc_snappy_level_6_bitshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_snappy_level_6_with_bitshuffle.h5','w')

f_Blosc_snappy_level_9_noshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_snappy_level_9_wo_shuffle.h5','w')
f_Blosc_snappy_level_9_byteshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_snappy_level_9_with_shuffle.h5','w')
f_Blosc_snappy_level_9_bitshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_snappy_level_9_with_bitshuffle.h5','w')

########
f_Blosc_zlib_level_6_noshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_zlib_level_6_wo_shuffle.h5','w')
f_Blosc_zlib_level_6_byteshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_zlib_level_6_with_shuffle.h5','w')
f_Blosc_zlib_level_6_bitshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_zlib_level_6_with_bitshuffle.h5','w')

f_Blosc_zlib_level_9_noshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_zlib_level_9_wo_shuffle.h5','w')
f_Blosc_zlib_level_9_byteshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_zlib_level_9_with_shuffle.h5','w')
f_Blosc_zlib_level_9_bitshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_zlib_level_9_with_bitshuffle.h5','w')

########
f_Blosc_zstd_level_6_noshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_zstd_level_6_wo_shuffle.h5','w')
f_Blosc_zstd_level_6_byteshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_zstd_level_6_with_shuffle.h5','w')
f_Blosc_zstd_level_6_bitshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_zstd_level_6_with_bitshuffle.h5','w')

f_Blosc_zstd_level_9_noshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_zstd_level_9_wo_shuffle.h5','w')
f_Blosc_zstd_level_9_byteshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_zstd_level_9_with_shuffle.h5','w')
f_Blosc_zstd_level_9_bitshuffle = h5.File(filefrom.split('.')[0]+'_Blosc_zstd_level_9_with_bitshuffle.h5','w')

########
f_zfp = h5.File(filefrom.split('.')[0]+'_zfp_reversible.h5','w')

########
f_bitshuffle_lz4_wo = h5.File(filefrom.split('.')[0]+'_bitshuffle_lz4_wo.h5','w')
f_bitshuffle_lz4_with = h5.File(filefrom.split('.')[0]+'_bitshuffle_lz4_with.h5','w')

########
f_lz4_nbytes0 = h5.File(filefrom.split('.')[0]+'_lz4_nbytes0.h5','w')
f_lz4_nbytes2048 = h5.File(filefrom.split('.')[0]+'_lz4_nbytes2048.h5','w')
f_lz4_nbytes16384 = h5.File(filefrom.split('.')[0]+'_lz4_nbytes16384.h5','w')

#########
f_zstd = h5.File(filefrom.split('.')[0]+'_zstd.h5','w')


############
path_to_data = '/data/data'

d_gzip_level6_wo = f_gzip_level6_wo.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, compression="gzip", compression_opts=6, shuffle=False)
d_gzip_level6_with = f_gzip_level6_with.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, compression="gzip", compression_opts=6, shuffle=True)
d_gzip_level9_wo = f_gzip_level9_wo.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, compression="gzip", compression_opts=9, shuffle=False)
d_gzip_level9_with = f_gzip_level9_with.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, compression="gzip", compression_opts=9, shuffle=True)


########
d_lzf_wo = f_lzf_wo.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, compression="lzf", shuffle=False)
d_lzf_with = f_lzf_with.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, compression="lzf", shuffle=True)

########
d_Blosc_lz4_level_6_noshuffle = f_Blosc_lz4_level_6_noshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='lz4', clevel=6, shuffle=hdf5plugin.Blosc.NOSHUFFLE))
d_Blosc_lz4_level_6_byteshuffle = f_Blosc_lz4_level_6_byteshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='lz4', clevel=6, shuffle=hdf5plugin.Blosc.SHUFFLE))
d_Blosc_lz4_level_6_bitshuffle = f_Blosc_lz4_level_6_bitshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='lz4', clevel=6, shuffle=hdf5plugin.Blosc.BITSHUFFLE))

d_Blosc_lz4_level_9_noshuffle = f_Blosc_lz4_level_9_noshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='lz4', clevel=9, shuffle=hdf5plugin.Blosc.NOSHUFFLE))
d_Blosc_lz4_level_9_byteshuffle = f_Blosc_lz4_level_9_byteshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='lz4', clevel=9, shuffle=hdf5plugin.Blosc.SHUFFLE))
d_Blosc_lz4_level_9_bitshuffle = f_Blosc_lz4_level_9_bitshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='lz4', clevel=9, shuffle=hdf5plugin.Blosc.BITSHUFFLE))


########
d_Blosc_lz4hc_level_6_noshuffle = f_Blosc_lz4hc_level_6_noshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='lz4hc', clevel=6, shuffle=hdf5plugin.Blosc.NOSHUFFLE))
d_Blosc_lz4hc_level_6_byteshuffle = f_Blosc_lz4hc_level_6_byteshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='lz4hc', clevel=6, shuffle=hdf5plugin.Blosc.SHUFFLE))
d_Blosc_lz4hc_level_6_bitshuffle = f_Blosc_lz4hc_level_6_bitshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='lz4hc', clevel=6, shuffle=hdf5plugin.Blosc.BITSHUFFLE))

d_Blosc_lz4hc_level_9_noshuffle = f_Blosc_lz4hc_level_9_noshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='lz4hc', clevel=9, shuffle=hdf5plugin.Blosc.NOSHUFFLE))
d_Blosc_lz4hc_level_9_byteshuffle = f_Blosc_lz4hc_level_9_byteshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='lz4hc', clevel=9, shuffle=hdf5plugin.Blosc.SHUFFLE))
d_Blosc_lz4hc_level_9_bitshuffle = f_Blosc_lz4hc_level_9_bitshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='lz4hc', clevel=9, shuffle=hdf5plugin.Blosc.BITSHUFFLE))


########
d_Blosc_blosclz_level_6_noshuffle = f_Blosc_blosclz_level_6_noshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='blosclz', clevel=6, shuffle=hdf5plugin.Blosc.NOSHUFFLE))
d_Blosc_blosclz_level_6_byteshuffle = f_Blosc_blosclz_level_6_byteshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='blosclz', clevel=6, shuffle=hdf5plugin.Blosc.SHUFFLE))
d_Blosc_blosclz_level_6_bitshuffle = f_Blosc_blosclz_level_6_bitshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='blosclz', clevel=6, shuffle=hdf5plugin.Blosc.BITSHUFFLE))

d_Blosc_blosclz_level_9_noshuffle = f_Blosc_blosclz_level_9_noshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='blosclz', clevel=9, shuffle=hdf5plugin.Blosc.NOSHUFFLE))
d_Blosc_blosclz_level_9_byteshuffle = f_Blosc_blosclz_level_9_byteshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='blosclz', clevel=9, shuffle=hdf5plugin.Blosc.SHUFFLE))
d_Blosc_blosclz_level_9_bitshuffle = f_Blosc_blosclz_level_9_bitshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='blosclz', clevel=9, shuffle=hdf5plugin.Blosc.BITSHUFFLE))


########
d_Blosc_snappy_level_6_noshuffle = f_Blosc_snappy_level_6_noshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='snappy', clevel=6, shuffle=hdf5plugin.Blosc.NOSHUFFLE))
d_Blosc_snappy_level_6_byteshuffle = f_Blosc_snappy_level_6_byteshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='snappy', clevel=6, shuffle=hdf5plugin.Blosc.SHUFFLE))
d_Blosc_snappy_level_6_bitshuffle = f_Blosc_snappy_level_6_bitshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='snappy', clevel=6, shuffle=hdf5plugin.Blosc.BITSHUFFLE))

d_Blosc_snappy_level_9_noshuffle = f_Blosc_snappy_level_9_noshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='snappy', clevel=9, shuffle=hdf5plugin.Blosc.NOSHUFFLE))
d_Blosc_snappy_level_9_byteshuffle = f_Blosc_snappy_level_9_byteshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='snappy', clevel=9, shuffle=hdf5plugin.Blosc.SHUFFLE))
d_Blosc_snappy_level_9_bitshuffle = f_Blosc_snappy_level_9_bitshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='snappy', clevel=9, shuffle=hdf5plugin.Blosc.BITSHUFFLE))

########
d_Blosc_zlib_level_6_noshuffle = f_Blosc_zlib_level_6_noshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='zlib', clevel=6, shuffle=hdf5plugin.Blosc.NOSHUFFLE))
d_Blosc_zlib_level_6_byteshuffle = f_Blosc_zlib_level_6_byteshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='zlib', clevel=6, shuffle=hdf5plugin.Blosc.SHUFFLE))
d_Blosc_zlib_level_6_bitshuffle = f_Blosc_zlib_level_6_bitshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='zlib', clevel=6, shuffle=hdf5plugin.Blosc.BITSHUFFLE))

d_Blosc_zlib_level_9_noshuffle = f_Blosc_zlib_level_9_noshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='zlib', clevel=9, shuffle=hdf5plugin.Blosc.NOSHUFFLE))
d_Blosc_zlib_level_9_byteshuffle = f_Blosc_zlib_level_9_byteshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='zlib', clevel=9, shuffle=hdf5plugin.Blosc.SHUFFLE))
d_Blosc_zlib_level_9_bitshuffle = f_Blosc_zlib_level_9_bitshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='zlib', clevel=9, shuffle=hdf5plugin.Blosc.BITSHUFFLE))

########
d_Blosc_zstd_level_6_noshuffle = f_Blosc_zstd_level_6_noshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='zstd', clevel=6, shuffle=hdf5plugin.Blosc.NOSHUFFLE))
d_Blosc_zstd_level_6_byteshuffle = f_Blosc_zstd_level_6_byteshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='zstd', clevel=6, shuffle=hdf5plugin.Blosc.SHUFFLE))
d_Blosc_zstd_level_6_bitshuffle = f_Blosc_zstd_level_6_bitshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='zstd', clevel=6, shuffle=hdf5plugin.Blosc.BITSHUFFLE))

d_Blosc_zstd_level_9_noshuffle = f_Blosc_zstd_level_9_noshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='zstd', clevel=9, shuffle=hdf5plugin.Blosc.NOSHUFFLE))
d_Blosc_zstd_level_9_byteshuffle = f_Blosc_zstd_level_9_byteshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='zstd', clevel=9, shuffle=hdf5plugin.Blosc.SHUFFLE))
d_Blosc_zstd_level_9_bitshuffle = f_Blosc_zstd_level_9_bitshuffle.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Blosc(cname='zstd', clevel=9, shuffle=hdf5plugin.Blosc.BITSHUFFLE))

########
d_zfp = f_zfp.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Zfp(reversible=True))

########
d_bitshuffle_lz4_wo = f_bitshuffle_lz4_wo.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Bitshuffle(nelems=0, lz4=False))
d_bitshuffle_lz4_with = f_bitshuffle_lz4_with.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Bitshuffle(nelems=0, lz4=True))

########
d_lz4_nbytes0 = f_lz4_nbytes0.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.LZ4(nbytes=0))
d_lz4_nbytes2048 = f_lz4_nbytes2048.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.LZ4(nbytes=2048))
d_lz4_nbytes16384 = f_lz4_nbytes16384.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.LZ4(nbytes=16384))



d_zstd = f_zstd.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, **hdf5plugin.Zstd())

###########

d_gzip_level6_wo[0,] = data[0,]
d_gzip_level6_with[0,] = data[0,]
d_gzip_level9_wo[0,] = data[0,]
d_gzip_level9_with[0,] = data[0,]



#########
d_lzf_wo[0,] = data[0,]
d_lzf_with[0,] = data[0,]

#########
d_Blosc_lz4_level_6_noshuffle[0,] = data[0,]
d_Blosc_lz4_level_6_byteshuffle[0,] = data[0,]
d_Blosc_lz4_level_6_bitshuffle[0,] = data[0,]

d_Blosc_lz4_level_9_noshuffle[0,] = data[0,]
d_Blosc_lz4_level_9_byteshuffle[0,] = data[0,]
d_Blosc_lz4_level_9_bitshuffle[0,] = data[0,]


#########
d_Blosc_lz4hc_level_6_noshuffle[0,] = data[0,]
d_Blosc_lz4hc_level_6_byteshuffle[0,] = data[0,]
d_Blosc_lz4hc_level_6_bitshuffle[0,] = data[0,]

d_Blosc_lz4hc_level_9_noshuffle[0,] = data[0,]
d_Blosc_lz4hc_level_9_byteshuffle[0,] = data[0,]
d_Blosc_lz4hc_level_9_bitshuffle[0,] = data[0,]


#########
d_Blosc_blosclz_level_6_noshuffle[0,] = data[0,]
d_Blosc_blosclz_level_6_byteshuffle[0,] = data[0,]
d_Blosc_blosclz_level_6_bitshuffle[0,] = data[0,]

d_Blosc_blosclz_level_9_noshuffle[0,] = data[0,]
d_Blosc_blosclz_level_9_byteshuffle[0,] = data[0,]
d_Blosc_blosclz_level_9_bitshuffle[0,] = data[0,]

#########
d_Blosc_snappy_level_6_noshuffle[0,] = data[0,]
d_Blosc_snappy_level_6_byteshuffle[0,] = data[0,]
d_Blosc_snappy_level_6_bitshuffle[0,] = data[0,]

d_Blosc_snappy_level_9_noshuffle[0,] = data[0,]
d_Blosc_snappy_level_9_byteshuffle[0,] = data[0,]
d_Blosc_snappy_level_9_bitshuffle[0,] = data[0,]

#########
d_Blosc_zlib_level_6_noshuffle[0,] = data[0,]
d_Blosc_zlib_level_6_byteshuffle[0,] = data[0,]
d_Blosc_zlib_level_6_bitshuffle[0,] = data[0,]

d_Blosc_zlib_level_9_noshuffle[0,] = data[0,]
d_Blosc_zlib_level_9_byteshuffle[0,] = data[0,]
d_Blosc_zlib_level_9_bitshuffle[0,] = data[0,]


#########
d_Blosc_zstd_level_6_noshuffle[0,] = data[0,]
d_Blosc_zstd_level_6_byteshuffle[0,] = data[0,]
d_Blosc_zstd_level_6_bitshuffle[0,] = data[0,]

d_Blosc_zstd_level_9_noshuffle[0,] = data[0,]
d_Blosc_zstd_level_9_byteshuffle[0,] = data[0,]
d_Blosc_zstd_level_9_bitshuffle[0,] = data[0,]

#########
d_zfp[0,] = data[0,]
d_bitshuffle_lz4_wo[0,] = data[0,]
d_bitshuffle_lz4_with[0,] = data[0,]

d_lz4_nbytes0[0,] = data[0,]
d_lz4_nbytes2048[0,] = data[0,]
d_lz4_nbytes16384[0,] = data[0,]

d_zstd[0,] = data[0,]

for i in range(num):

    d_gzip_level6_wo.resize((i+1,) + shape_data)
    d_gzip_level6_with.resize((i+1,) + shape_data)
    d_gzip_level6_wo[i,] = data[i,]
    d_gzip_level6_with[i,] = data[i,]
    
    d_gzip_level9_wo.resize((i+1,) + shape_data)
    d_gzip_level9_with.resize((i+1,) + shape_data)
    d_gzip_level9_wo[i,] = data[i,]
    d_gzip_level9_with[i,] = data[i,]
    
    
    #########
    d_lzf_wo.resize((i+1,) + shape_data)
    d_lzf_with.resize((i+1,) + shape_data)
    d_lzf_wo[i,] = data[i,]
    d_lzf_with[i,] = data[i,]
    
    #########
    d_Blosc_lz4_level_6_noshuffle.resize((i+1,) + shape_data)
    d_Blosc_lz4_level_6_byteshuffle.resize((i+1,) + shape_data)
    d_Blosc_lz4_level_6_bitshuffle.resize((i+1,) + shape_data)
    d_Blosc_lz4_level_6_noshuffle[i,] = data[i,] 
    d_Blosc_lz4_level_6_byteshuffle[i,] = data[i,]
    d_Blosc_lz4_level_6_bitshuffle[i,] = data[i,]
    
    d_Blosc_lz4_level_9_noshuffle.resize((i+1,) + shape_data)
    d_Blosc_lz4_level_9_byteshuffle.resize((i+1,) + shape_data)
    d_Blosc_lz4_level_9_bitshuffle.resize((i+1,) + shape_data)
    d_Blosc_lz4_level_9_noshuffle[i,] = data[i,] 
    d_Blosc_lz4_level_9_byteshuffle[i,] = data[i,]
    d_Blosc_lz4_level_9_bitshuffle[i,] = data[i,]
    
    #########
    d_Blosc_lz4hc_level_6_noshuffle.resize((i+1,) + shape_data)
    d_Blosc_lz4hc_level_6_byteshuffle.resize((i+1,) + shape_data)
    d_Blosc_lz4hc_level_6_bitshuffle.resize((i+1,) + shape_data)
    d_Blosc_lz4hc_level_6_noshuffle[i,] = data[i,] 
    d_Blosc_lz4hc_level_6_byteshuffle[i,] = data[i,] 
    d_Blosc_lz4hc_level_6_bitshuffle[i,] = data[i,] 

    d_Blosc_lz4hc_level_9_noshuffle.resize((i+1,) + shape_data)
    d_Blosc_lz4hc_level_9_byteshuffle.resize((i+1,) + shape_data)
    d_Blosc_lz4hc_level_9_bitshuffle.resize((i+1,) + shape_data)
    d_Blosc_lz4hc_level_9_noshuffle[i,] = data[i,] 
    d_Blosc_lz4hc_level_9_byteshuffle[i,] = data[i,] 
    d_Blosc_lz4hc_level_9_bitshuffle[i,] = data[i,]
    
    
    #########
    d_Blosc_blosclz_level_6_noshuffle.resize((i+1,) + shape_data)
    d_Blosc_blosclz_level_6_byteshuffle.resize((i+1,) + shape_data)
    d_Blosc_blosclz_level_6_bitshuffle.resize((i+1,) + shape_data)
    d_Blosc_blosclz_level_6_noshuffle[i,] = data[i,]
    d_Blosc_blosclz_level_6_byteshuffle[i,] = data[i,]
    d_Blosc_blosclz_level_6_bitshuffle[i,] = data[i,]

    d_Blosc_blosclz_level_9_noshuffle.resize((i+1,) + shape_data)
    d_Blosc_blosclz_level_9_byteshuffle.resize((i+1,) + shape_data)
    d_Blosc_blosclz_level_9_bitshuffle.resize((i+1,) + shape_data)
    d_Blosc_blosclz_level_9_noshuffle[i,] = data[i,]
    d_Blosc_blosclz_level_9_byteshuffle[i,] = data[i,]
    d_Blosc_blosclz_level_9_bitshuffle[i,] = data[i,]
    
    #########
    d_Blosc_snappy_level_6_noshuffle.resize((i+1,) + shape_data)
    d_Blosc_snappy_level_6_byteshuffle.resize((i+1,) + shape_data)
    d_Blosc_snappy_level_6_bitshuffle.resize((i+1,) + shape_data)
    d_Blosc_snappy_level_6_noshuffle[i,] = data[i,]
    d_Blosc_snappy_level_6_byteshuffle[i,] = data[i,]
    d_Blosc_snappy_level_6_bitshuffle[i,] = data[i,]

    d_Blosc_snappy_level_9_noshuffle.resize((i+1,) + shape_data)
    d_Blosc_snappy_level_9_byteshuffle.resize((i+1,) + shape_data)
    d_Blosc_snappy_level_9_bitshuffle.resize((i+1,) + shape_data)
    d_Blosc_snappy_level_9_noshuffle[i,] = data[i,]
    d_Blosc_snappy_level_9_byteshuffle[i,] = data[i,]
    d_Blosc_snappy_level_9_bitshuffle[i,] = data[i,]

    #########
    d_Blosc_zlib_level_6_noshuffle.resize((i+1,) + shape_data)
    d_Blosc_zlib_level_6_byteshuffle.resize((i+1,) + shape_data)
    d_Blosc_zlib_level_6_bitshuffle.resize((i+1,) + shape_data)
    d_Blosc_zlib_level_6_noshuffle[i,] = data[i,]
    d_Blosc_zlib_level_6_byteshuffle[i,] = data[i,]
    d_Blosc_zlib_level_6_bitshuffle[i,] = data[i,]

    d_Blosc_zlib_level_9_noshuffle.resize((i+1,) + shape_data)
    d_Blosc_zlib_level_9_byteshuffle.resize((i+1,) + shape_data)
    d_Blosc_zlib_level_9_bitshuffle.resize((i+1,) + shape_data)
    d_Blosc_zlib_level_9_noshuffle[i,] = data[i,]
    d_Blosc_zlib_level_9_byteshuffle[i,] = data[i,]
    d_Blosc_zlib_level_9_bitshuffle[i,] = data[i,]
    
    #########
    d_Blosc_zstd_level_6_noshuffle.resize((i+1,) + shape_data)
    d_Blosc_zstd_level_6_byteshuffle.resize((i+1,) + shape_data)
    d_Blosc_zstd_level_6_bitshuffle.resize((i+1,) + shape_data)
    d_Blosc_zstd_level_6_noshuffle[i,] = data[i,]
    d_Blosc_zstd_level_6_byteshuffle[i,] = data[i,]
    d_Blosc_zstd_level_6_bitshuffle[i,] = data[i,]

    d_Blosc_zstd_level_9_noshuffle.resize((i+1,) + shape_data)
    d_Blosc_zstd_level_9_byteshuffle.resize((i+1,) + shape_data)
    d_Blosc_zstd_level_9_bitshuffle.resize((i+1,) + shape_data)
    d_Blosc_zstd_level_9_noshuffle[i,] = data[i,]
    d_Blosc_zstd_level_9_byteshuffle[i,] = data[i,]
    d_Blosc_zstd_level_9_bitshuffle[i,] = data[i,]
    
    #########
    d_zfp.resize((i+1,) + shape_data)
    d_zfp[i,] = data[i,]
    d_bitshuffle_lz4_wo.resize((i+1,) + shape_data)
    d_bitshuffle_lz4_with.resize((i+1,) + shape_data)
    d_bitshuffle_lz4_wo[i,] = data[i,]
    d_bitshuffle_lz4_with[i,] = data[i,]
    
    #########
    d_lz4_nbytes0.resize((i+1,) + shape_data)
    d_lz4_nbytes2048.resize((i+1,) + shape_data)
    d_lz4_nbytes16384.resize((i+1,) + shape_data)
    d_lz4_nbytes0[i,] = data[i,]
    d_lz4_nbytes2048[i,] = data[i,]
    d_lz4_nbytes16384[i,] = data[i,]
    
    d_zstd.resize((i+1,) + shape_data)
    d_zstd[i,] = data[i,]
    

f_gzip_level6_wo.close()
f_gzip_level6_with.close()
f_gzip_level9_wo.close()
f_gzip_level9_with.close()


f_lzf_wo.close()
f_lzf_with.close()


f_Blosc_lz4_level_6_noshuffle.close()
f_Blosc_lz4_level_6_bitshuffle.close()
f_Blosc_lz4_level_6_byteshuffle.close()

f_Blosc_lz4_level_9_noshuffle.close()
f_Blosc_lz4_level_9_bitshuffle.close()
f_Blosc_lz4_level_9_byteshuffle.close()


f_Blosc_lz4hc_level_6_noshuffle.close()
f_Blosc_lz4hc_level_6_bitshuffle.close()
f_Blosc_lz4hc_level_6_byteshuffle.close()

f_Blosc_lz4hc_level_9_noshuffle.close()
f_Blosc_lz4hc_level_9_bitshuffle.close()
f_Blosc_lz4hc_level_9_byteshuffle.close()


f_Blosc_blosclz_level_6_noshuffle.close()
f_Blosc_blosclz_level_6_bitshuffle.close()
f_Blosc_blosclz_level_6_byteshuffle.close()

f_Blosc_blosclz_level_9_noshuffle.close()
f_Blosc_blosclz_level_9_bitshuffle.close()
f_Blosc_blosclz_level_9_byteshuffle.close()


f_Blosc_snappy_level_6_noshuffle.close()
f_Blosc_snappy_level_6_bitshuffle.close()
f_Blosc_snappy_level_6_byteshuffle.close()

f_Blosc_snappy_level_9_noshuffle.close()
f_Blosc_snappy_level_9_bitshuffle.close()
f_Blosc_snappy_level_9_byteshuffle.close()

f_Blosc_zlib_level_6_noshuffle.close()
f_Blosc_zlib_level_6_bitshuffle.close()
f_Blosc_zlib_level_6_byteshuffle.close()

f_Blosc_zlib_level_9_noshuffle.close()
f_Blosc_zlib_level_9_bitshuffle.close()
f_Blosc_zlib_level_9_byteshuffle.close()


f_Blosc_zstd_level_6_noshuffle.close()
f_Blosc_zstd_level_6_bitshuffle.close()
f_Blosc_zstd_level_6_byteshuffle.close()

f_Blosc_zstd_level_9_noshuffle.close()
f_Blosc_zstd_level_9_bitshuffle.close()
f_Blosc_zstd_level_9_byteshuffle.close()


f_zfp.close()
f_bitshuffle_lz4_wo.close()
f_bitshuffle_lz4_with.close()

f_lz4_nbytes0.close()
f_lz4_nbytes2048.close()
f_lz4_nbytes16384.close()

f_zstd.close()

f.close()
