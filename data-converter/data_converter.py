#!/usr/bin/env python3
# coding: utf8
"""
python3 data_converter.py -i <data_filename>.h5 -p /path_to_data/data -m /path_to_mask/mask

python3 data_converter.py -i EuXFEL-S00008-r0096-c04.cxi -p /entry_1/instrument_1/detector_1/detector_corrected/data -m /entry_1/instrument_1/detector_1/detector_corrected/mask

python3 data_converter.py -i r0108.cxi -p /entry_1/instrument_1/detector_1/data -m /entry_1/instrument_1/detector_1/mask
"""

import sys
import os
import h5py as h5
import numpy as np
import argparse
from multiprocessing import Pool

os.nice(0)

os.nice(0)

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-i', '--input', nargs='+', type=str, help="List of cxi files")
    parser.add_argument('-f', '--file', type=str, help="File with the list of cxi files")
    parser.add_argument('-p', type=str, help="hdf5 path for the cxi file data")
    parser.add_argument('-m', type=str, help="hdf5 path for the cxi file mask")
    return parser.parse_args()

def converter(filename):
    global path_cxi
    global path_mask

    outPrefix = 'converted-' + filename
    print('Starting converting {}'.format(filename))

    with h5.File(filename, 'r') as in_f, h5.File(outPrefix, 'w') as out_f:
        mask = in_f[path_mask]
        data = in_f[path_cxi]

        shape = data.shape
        num = shape[0]
        print('Previous shape is {}'.format(shape))

        if len(shape[1:]) == 2:
            new_shape = (shape[1] // 512, 512, shape[2]) # from Cheetah (8192, 128) to vds (16,512,128)

        else:
            new_shape = (shape[1] * shape[2], shape[3]) #from vds (16,512,128) to Cheetah (8192, 128)

        chunks_shape = (1,) + new_shape
        max_shape = (num,) + new_shape
        print('New shape is {}'.format(new_shape))

        d = out_f.create_dataset(path_cxi, chunks_shape, maxshape=max_shape, dtype=np.float32, chunks=chunks_shape, compression="gzip", compression_opts=4)
        m = out_f.create_dataset(path_mask, chunks_shape, maxshape=max_shape, dtype=np.float32, chunks=chunks_shape, compression="gzip", compression_opts=4)

        tmp_mask = np.array([np.reshape(mask[0,].ravel(), new_shape)])
        tmp_data = np.array([np.reshape(data[0,].ravel(), new_shape)])

        d[0,] = tmp_data
        m[0,] = tmp_mask

        for i in range(num):
            new_size = (i+1,) + new_shape

            d.resize(new_size)
            m.resize(new_size)

            tmp_mask = np.array([np.reshape(mask[i,].ravel(), new_shape)])
            tmp_data = np.array([np.reshape(data[i,].ravel(), new_shape)])
            print(tmp_data.shape, tmp_mask.shape)

            d[i,] = tmp_data
            m[i,] = tmp_mask




if __name__ == "__main__":
    args = parse_cmdline_args()

    list_of_cxi_files = []

    if args.input is not None:
        list_of_cxi_files = args.input
    else:
        try:
            with open(args.file, 'r') as f:
                for line in f:
                    list_of_cxi_files.append(line.strip())
        except:
            print("It's necessary to give a list of files or stream with them as input parameter.\n")


    path_cxi = args.p
    path_mask = args.m

    pool = Pool() # multiprocessing.Pool
    pool.map(converter, list_of_cxi_files)
    print('Finish')