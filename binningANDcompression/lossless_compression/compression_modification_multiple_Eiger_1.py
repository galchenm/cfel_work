import itertools
import h5py
import hdf5plugin
import numpy as np
import pandas as pd
from skimage.io import imread
import io
from pathlib import Path
import time
from collections import namedtuple
import matplotlib.pyplot as plt
import os
import sys
import glob

Timings = namedtuple("Timings", ["min", "max", "mean", "median"])

output = '/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/lossless_compression/test_on_multiple_image_results_all_levels'

if not os.path.exists(output):
    os.mkdir(output)

def print_timings(timings):
    print("min =", timings.min)
    print("max =", timings.max)
    print("mean =", timings.mean)
    print("median =", timings.median)


# functions to obtain compression options
def zlib_opts(level=4):
    """zlib compression options

    level must be an integer from 0 to 9
    """
    return lambda data: dict(compression="gzip", compression_opts=level)


def bzip2_opts(blocksize=9):
    """bzip2 compression options

    blocksize must be an integer from 1 to 9 and specifies the block size in 100k bytes
    """
    return lambda data: dict(compression=307, compression_opts=(blocksize,))


def lzf_opts():
    """lzf compression options

    lzf does not have further options"""
    return lambda data: dict(compression="lzf")


def bitshuffle_opts(nelems=0, complib="lz4"):
    """bitshuffle compression options

    nelems is the number of elements per block, 0 is the default of about 8kb per block,
    complib must be "lz4"
    """
    if complib == "lz4":
        clib = 2
    else:
        raise ValueError(f"Unsupported compression name '{complib}'")
    # from https://indico.esrf.fr/indico/event/12/session/0/contribution/2/material/slides/0.odp  # noqa
    return lambda data: dict(compression=32008, compression_opts=(nelems, clib))


def zfp_opts(accuracy=0.001):
    """zfp compression options

    zfp is a lossy compression algorithm, accuracy sets the desired absolute error
    """
    return lambda data: dict(
        **hdf5plugin.Zfp(accuracy=accuracy)
    )  # many more options available


def blosc_opts(level=5, complib="lz4", shuffle="byte"):
    """Options for the blosc family of compression algorithms

    HDF5 shuffle should be disabled if blosc "byte" or "bit" shuffle is used

    Parameters:
    level: int
        Compression level from 0 (none) to 9 (best), default: 5
    complib: str
        One of "blosclz", "lz4", "lz4hc", "snappy", "zlib", or "zstd", default: lz4
    shuffle: str
        One of "none", "byte", "bit", default: "byte"
    """
    # from https://github.com/h5py/h5py/issues/611#issuecomment-353694301
    shuf = dict(none=0, byte=1, bit=2)[shuffle]
    compressors = ["blosclz", "lz4", "lz4hc", "snappy", "zlib", "zstd"]
    clib = compressors.index(complib)
    args = {
        "compression": 32001,
        "compression_opts": (0, 0, 0, 0, level, shuf, clib),
    }
    return lambda data: args


def jpeg_opts(quality=80):
    # jpeg_opts need shape information
    # see https://github.com/CARS-UChicago/jpegHDF5
    def get_opts(data):
        if data.ndim != 2:
            raise ValueError("Only 2D images are supported for jpeg compression")
        if data.itemsize != 1:
            # The jpeg filter would silently store the raw data without compression
            raise ValueError(
                "Only 8 bit monochrome images are supported for jpeg compression"
            )
        return dict(compression=32019, compression_opts=(quality, *data.shape, 0))

    return get_opts


def compress_data(io, data, opts):
    with h5py.File(io, "w") as f:
        f.create_dataset("data", data=data, chunks=data.shape, **opts(data))


def decompress_data(io):
    with h5py.File(io) as f:
        return f["data"][:]


def time_compression(data, opts, number=100):
    times = []
    for i in range(number):
        buf = io.BytesIO()
        start = time.time()
        compress_data(buf, data, opts)
        elapsed = time.time() - start
        times.append(elapsed)
    return Timings(
        mean=np.mean(times),
        median=np.median(times),
        min=np.min(times),
        max=np.max(times),
    )


def time_decompression(io, number=100):
    times = []
    for i in range(number):
        start = time.time()
        decompress_data(io)
        elapsed = time.time() - start
        times.append(elapsed)
    return Timings(
        mean=np.mean(times),
        median=np.median(times),
        min=np.min(times),
        max=np.max(times),
    )


def time_all(image, opts, name, number=10, image_name="test"):
    print("Writing with {}:".format(name))
    timings_comp = time_compression(image, opts, number)

    print_timings(timings_comp)

    buf = io.BytesIO()
    compress_data(buf, image, opts)

    timings_decomp = time_decompression(buf, number)

    print()
    print("Reading with {}:".format(name))
    print_timings(timings_decomp)

    decomp_image = decompress_data(buf)
    if not np.allclose(decomp_image, image, atol=0.005):
        diff = np.abs(decomp_image - image)
        i, j = np.unravel_index(np.argmax(diff), image.shape)
        with open(image_name + "_" + name.replace(" ", "_") + ".h5", "wb") as f:
            f.write(buf.getvalue())
        raise ValueError(
            "Decompressed image differs by a maximum of " f"{diff[i, j]} at [{i}, {j}]"
        )

    return timings_comp, timings_decomp, buf.getbuffer().nbytes



def get_images_from_hdf5(path, dataset):
    file = h5py.File(path)
    dataset = file[dataset][()]
    print(dataset.shape)
    return dataset

def benchmark_image(name, image_name, image, algorithms):
    alg_names = ["no compression"] + [a[0] for a in algorithms]
    column_names = [
        "comp_size",
        "comp_ratio",
        "comp_time_min",
        "comp_time_max",
        "comp_time_mean",
        "comp_time_median",
        "comp_time_ratio",
        "decomp_time_min",
        "decomp_time_max",
        "decomp_time_mean",
        "decomp_time_median",
        "decomp_time_ratio",
    ]
    df = pd.DataFrame(index=alg_names, columns=column_names)
    df.name = f'{image_name}'
    df.index.name = "compression method"

    timings_comp, timings_decomp, size = time_all(
        image, lambda data: {}, "no compression", image_name=image_name
    )
    df.loc["no compression", :] = size, 1, *timings_comp, 1, *timings_decomp, 1

    min_time_comp = df.loc["no compression", "comp_time_min"]
    min_time_decomp = df.loc["no compression", "decomp_time_min"]
    orig_size = df.loc["no compression", "comp_size"]

    print()
    print()
    for alg_name, alg_opts, extra_opts in algorithms:
        try:
            timings_comp, timings_decomp, size = time_all(
                image, alg_opts, alg_name, image_name=image_name, **extra_opts
            )
        except ValueError as err:
            print()
            print("ERROR:", err)
            print()
            continue

        min_time_comp_alg = timings_comp.min
        min_time_decomp_alg = timings_decomp.min

        size_ratio = orig_size / size #size / orig_size #CR =  uncompressed / compressed
        comp_time_ratio = min_time_comp_alg / min_time_comp # I'm a bit confused about such formula
        decomp_time_ratio = min_time_decomp_alg / min_time_decomp

        df.loc[alg_name, :] = (
            size,
            size_ratio,
            *timings_comp,
            comp_time_ratio,
            *timings_decomp,
            decomp_time_ratio,
        )
        dd[name][alg_name]['comp_ratio'].append(size_ratio)
        dd[name][alg_name]['comp_time_ratio'].append(comp_time_ratio)
        dd[name][alg_name]['decomp_time_ratio'].append(decomp_time_ratio)
        
        print()
        print("time ratio compression   =", comp_time_ratio)
        print("time ratio decompression =", decomp_time_ratio)
        print("space ratio =", size_ratio)
        print()
        print()

    return df



def multiple_images():
    #get_images_from_hdf5
    dir = "/asap3/fs-sc/gpfs/scdd01/2022/data/11015175/scratch_cc/"


    #for file in Path(dir).glob("**/Eiger16M/**/*.h5"):
    #    name = file.stem
    #    yield name, get_images_from_hdf5(file, "/data/data")
    #dd = {} #for multiple
    
    #for file in Path(dir).glob("**/Eiger16M/**/*.h5"):
    #    name = file.stem
    for file in glob.glob("/asap3/fs-sc/gpfs/scdd01/2022/data/11015175/scratch_cc/galchenm/for_Tim/Eiger16M/low_photons/truncated_to_1_bit/Eiger16M*.h5"):
        name = os.path.basename(file).split('.')[0]
        dataset = get_images_from_hdf5(file, "/data/data")
        for index in range(dataset.shape[0]):
            print(name, index)
            yield name, dataset[index,]
        


def fill_dic():
    #get_images_from_hdf5
    dir = "/asap3/fs-sc/gpfs/scdd01/2022/data/11015175/scratch_cc/"


    #for file in Path(dir).glob("**/Eiger16M/**/*.h5"):
    #    name = file.stem
    #    dd[name] = {i[0]:{'marker':marker, 'color':color, 'comp_ratio':[], 'comp_time_ratio':[], 'decomp_time_ratio':[]} for (i,marker,color) in zip(algorithms, itertools.cycle(markers), itertools.cycle(colors))} 
        


    #for file in Path(dir).glob("**/Eiger16M/**/*.h5"):
    #    name = file.stem
    for file in glob.glob("/asap3/fs-sc/gpfs/scdd01/2022/data/11015175/scratch_cc/galchenm/for_Tim/Eiger16M/low_photons/truncated_to_1_bit/Eiger16M*.h5"):
        name = os.path.basename(file).split('.')[0]
        dd[name] = {i[0]:{ 'marker':marker, 'color':color, 'comp_ratio':[], 'comp_time_ratio':[], 'decomp_time_ratio':[]} for (i,marker,color) in zip(algorithms, itertools.cycle(markers), itertools.cycle(colors))}
        dd[name]['index'] = 0
        

        
def benchmark_multiple_images(images, algorithms):
    Path("multiple_image_benchmarks").mkdir(exist_ok=True)
    for (name, image) in images:
        index = dd[name]['index']
        image_name = f'{name.replace(" ", "_")}_{index}'
        print("-----------------------------")
        print("Results for {}".format(image_name))
        print("-----------------------------")
        print()

        df = benchmark_image(name, image_name, image, algorithms)
        df.to_csv(f"multiple_image_benchmarks/benchmark_{image_name}.csv")
        dd[name]['index'] += 1
        

def plotting(image_name):
    f, (ax_comp, ax_decomp) = plt.subplots(1, 2, sharey=True)
    f.set_figheight(6)
    f.set_figwidth(12)
    ax_comp.set_ylabel("compression space ratio")
    ax_comp.set_xlabel("compression time / seconds")
    ax_decomp.set_xlabel("decompression time / seconds")



    print()
    print()
    
    for (alg_name, alg_opts, extra_opts) in algorithms:
        space_ratio = np.mean(dd[image_name][alg_name]['comp_ratio']) #df.loc[alg_name, "comp_ratio"]
        min_time_comp_alg = np.mean(dd[image_name][alg_name]['comp_time_ratio']) #df.loc[alg_name, "comp_time_ratio"]
        min_time_decomp_alg = np.mean(dd[image_name][alg_name]['decomp_time_ratio']) #df.loc[alg_name, "decomp_time_ratio"]
        marker = dd[image_name][alg_name]['marker']
        color = dd[image_name][alg_name]['color']
        ax_comp.plot(
            min_time_comp_alg, space_ratio, marker, color=color, label=alg_name
        )
        ax_decomp.plot(min_time_decomp_alg, space_ratio, marker, color=color)


    ax_comp.legend()

    plt.tight_layout(0.2, 0.2, 0.2)

    
    plt.savefig(os.path.join(output, "plot_{}.png".format(image_name)))
    
# algorithms

algorithms = [
    ("zlib", zlib_opts(), {"number": 10}),
    ("lz4 + bitshuffle", bitshuffle_opts(), {}),
    ("blosc:lz4 + w/o shuffle", blosc_opts(shuffle="none"), {}),
    ("blosc:lz4 + byteshuffle", blosc_opts(), {}),
    ("blosc:lz4 + bitshuffle", blosc_opts(shuffle="bit"), {}),
    ("blosc:blosclz + w/o shuffle", blosc_opts(complib="blosclz", shuffle="none"), {}),
    ("blosc:blosclz + byteshuffle", blosc_opts(complib="blosclz"), {}),
    ("blosc:blosclz + bitshuffle", blosc_opts(complib="blosclz", shuffle="bit"), {}),
    ("blosc:lz4hc + w/o shuffle", blosc_opts(complib="lz4hc", shuffle="none"), {}),
    ("blosc:lz4hc + byteshuffle", blosc_opts(complib="lz4hc"), {}),
    ("blosc:lz4hc + bitshuffle", blosc_opts(complib="lz4hc", shuffle="bit"), {}),
    ("blosc:zstd + w/o shuffle",blosc_opts(level=2, complib="zstd", shuffle="none"),{"number": 10},),
    ("blosc:zstd + byteshuffle",blosc_opts(level=2, complib="zstd"),{"number": 10},),
    ("blosc:zstd + bitshuffle",blosc_opts(level=2, complib="zstd", shuffle="bit"),{"number": 10},),
    ("bzip2", bzip2_opts(), {"number": 3}),
    ("lzf", lzf_opts(), {}),
]
'''

algorithms = [
    ("zlib", zlib_opts(), {"number": 10}),
]
'''
markers = ["v", "^", ">", "<", "P", "X", "s", "D", "p", "*"]
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k'] #["black", "blue", "red", "green"]


dd = {}

fill_dic()


benchmark_multiple_images(multiple_images(), algorithms)
d = {}
for image_name in dd:
    plotting(image_name)


for image_name in dd:
    d[image_name] = {}
    for (alg_name, alg_opts, extra_opts) in algorithms:
        d[image_name][alg_name] = {'Total number': dd[image_name]['index'], 'Mean space ratio': np.mean(dd[image_name][alg_name]['comp_ratio']),'Mean time ratio compression': np.mean(dd[image_name][alg_name]['comp_time_ratio']),'Mean time ratio decompression': np.mean(dd[image_name][alg_name]['decomp_time_ratio'])}
                                    

df = pd.DataFrame.from_dict(d, orient='index')
df.to_csv('total_info_for_multiple_images_Eiger16M_lacta_int_1k_patterns_truncated_to_1_bit.csv')