#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Luca Gelisio"
__contact__ = "luca.gelisio@cfel.de"
__version__ = "0.01"
__date__ = "09/2020"
__status__ = "beta"
__license__ = "GPL v3+"

import argparse
import sys
import os
import time
import h5py
import tables

### command line
parser = argparse.ArgumentParser(description="Compress EIGER 16M data")

parser.add_argument("descriptor", help="The HDF5 file to be compressed")

parser.add_argument(
    "--key",
    metavar="",
    help="HDF5 key (default: %(default)s)",
    default="/entry/data/data",
)
parser.add_argument(
    "--output",
    metavar="DESCRIPTOR",
    help="The descriptor of the output file (default: %(default)s)",
    default="./compressed.h5",
)

parser.add_argument(
    "--chunks",
    metavar="",
    nargs=3,
    type=int,
    help="Chunk shape (default: %(default)s)",
    default=(1, 4362, 4148),
)

parser.add_argument(
    "--compression",
    metavar="METHOD",
    help="Compression method (default: %(default)s)",
    default="bzip2",
)
parser.add_argument(
    "--options",
    nargs="+",
    metavar="",
    help="Compression options (default: %(default)s)",
    default=(9,),
)

args = parser.parse_args()

# compression options
if args.options is not None:

    # for compressors expecting a single option
    if len(args.options) == 1:
        args.options = int(args.options[0])

    # for compressors expecting a tuple with two options
    else:
        args.options = (args.options[0], int(args.options[1]))

print("Invoked with:\n{}\n".format(args))

# all cores for Blosc
tables.parameters.MAX_BLOSC_THREADS = None

### read the dataset
if not os.path.exists(args.descriptor):
    raise FileNotFoundError("Unable to access {}...".format(args.descriptor))

t0 = time.time()

with h5py.File(args.descriptor, "r") as fh:
    dataset = fh[args.key][:]

original_size = os.stat(args.descriptor).st_size
reading_time = time.time() - t0

print(
    "Read '{}' ({:.1f} MB) in {:.1f} seconds...".format(
        args.descriptor, original_size / 1024 ** 2, reading_time
    )
)

### write the compressed dataset
t0 = time.time()

with tables.open_file(
    args.output,
    mode="w",
    filters=tables.Filters(
        complib=args.compression,
        complevel=args.options,
        shuffle=True,
        bitshuffle=True if args.compression.find("blosc") > -1 else False,
        fletcher32=True,
    ),
) as hdf:

    # the output file has this default structure
    group1 = hdf.create_group("/", "entry", "")
    group2 = hdf.create_group("/entry", "data", "")

    hdf.create_carray("/entry/data", "data", obj=dataset, chunkshape=tuple(args.chunks))

compressed_size = os.stat(args.output).st_size

print(
    "Wrote '{}' ({:.1f} MB) in {:.1f} seconds: compression ratio {:.3f}...".format(
        args.output,
        compressed_size / 1024 ** 2,
        time.time() - t0,
        compressed_size / original_size,
    )
)

sys.exit(0)
