import glob
import os
import sys

from multiprocessing import Pool, TimeoutError
import argparse

'''
filename = sys.argv[1]
path_to_data = sys.argv[2]
maskfilename = sys.argv[3]
h5maskpath = sys.argv[4]
min_pix_count = int(sys.argv[5])
output_path = sys.argv[6]

'''

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-s','--s', type=str, help="Single HDF5 file that you want to have a convertion")
    parser.add_argument('-p','--p', type=str, help="The path of folder/s that contain/s HDF5 files")
    parser.add_argument('-f','--f', type=str, help="The file contains HDF5 files of interest")
    parser.add_argument('-m', type=str, help="maskfile")
    
    parser.add_argument('-o', type=str, help="output folder")
    
    parser.add_argument('-h5p', type=str, help="h5path to data in .h5/cxi files")
    parser.add_argument('-h5pm', type=str, help="h5path to data in .h5/cxi maskfile")
    
    parser.add_argument('-n', type=int, help="min_pix_count")
    
    return parser.parse_args()



def binning(filename, path_to_data, maskfilename, h5maskpath, min_pix_count, output_path):
    job_file = filename.split('.')[0] + '.sh'
    with open(job_file, 'w+') as fh:
        fh.writelines("#!/bin/sh\n")
        fh.writelines("#SBATCH --job=%s.job\n" % os.path.basename(filename).split('.')[0])
        fh.writelines("#SBATCH --partition=upex\n")
        fh.writelines("#SBATCH --time=280:00:00\n")
        fh.writelines("#SBATCH --nodes=1\n")
        fh.writelines("#SBATCH --mem=500000\n")
        fh.writelines("module load anaconda3/5.2\n")
        command = f'python3 /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/binning-only/binning-only.py {filename} {path_to_data} {maskfilename} {h5maskpath} {min_pix_count} {output_path}'
        print(command)
        fh.writelines(command)
    os.system("sbatch %s" % job_file)



if __name__ == "__main__":
    args = parse_cmdline_args()
    path_to_data = args.h5p
    maskfilename = args.m
    h5maskpath = args.h5pm
    min_pix_count = args.n
    output_path = args.o
    
    
    if args.p is not None: #The path of folder/s that contain/s HDF5 files
        path_from = args.p
        for path, dirs, all_files in os.walk(path_from):
            
            for cdir in dirs:
                path_from_dir = os.path.join(path, cdir)
                if 'S000' not in cdir:
                    
                    files = glob.glob(os.path.join(path_from_dir, '*.cxi'))
                    if len(files) == 0:
                        files = glob.glob(os.path.join(path_from_dir, '*data*.h5'))
                    
                    if len(files) == 0:
                        files = glob.glob(os.path.join(path_from_dir, '*.h5'))
                    
                    if len(files) > 0:
                        for filename in files:
                            binning(filename, path_to_data, maskfilename, h5maskpath, min_pix_count, output_path)                                               
    elif args.f is not None:
        with open(args.f, 'r') as f:

            for filename in f:
                if len(filename.strip()) != 0:
                    binning(filename.strip(), path_to_data, maskfilename, h5maskpath, min_pix_count, output_path)
                    
    elif args.s is not None:
        filename = args.s
        binning(filename, path_to_data, maskfilename, h5maskpath, min_pix_count, output_path) 

    else:
        print("You need to provide the path or file with files for compression")    
           

