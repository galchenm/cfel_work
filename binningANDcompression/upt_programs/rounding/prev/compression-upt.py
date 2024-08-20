import glob
import os
import sys

from multiprocessing import Pool, TimeoutError
import argparse

'''
python3 /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/compression.py -p /gpfs/cfel/cxi/scratch/data/2018/EXFEL-2018-Barty-Mar-p002012/p2120-compressed -h5p /entry_1/instrument_1/detector_1/data -h5pTo /entry_1/instrument_1/detector_1/data_256new -n 256

python3 /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/compression.py -p /gpfs/cfel/cxi/scratch/data/2018/EXFEL-2018-Barty-Mar-p002012/p2120-compressed -h5p /entry_1/instrument_1/detector_1/data -h5pTo /entry_1/instrument_1/detector_1/data_sqrtN --sqrt True


python3 /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/compression.py -p /gpfs/cfel/cxi/scratch/data/2018/EXFEL-2018-Barty-Mar-p002012/p2120-compressed -h5p /entry_1/instrument_1/detector_1/data -h5pTo /entry_1/instrument_1/detector_1/data_log --log True

'''

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-p', type=str, help="The path of folder/s that contain/s HDF5 files")
    parser.add_argument('-h5p', type=str, help="h5path to data in .h5/cxi files")
    parser.add_argument('-h5pTo', type=str, help="h5path where to data in .h5/cxi files")
    parser.add_argument("--intf", default=False, action="store" , help="Use this flag if you want to sqrt compression")
    parser.add_argument("--old", default=False, action="store" , help="Use this flag if you want to sqrt compression")
    parser.add_argument("--sqrt", default=False, action="store" , help="Use this flag if you want to sqrt compression")
    parser.add_argument("--log", default=False, action="store" , help="Use this flag if you want to log compression")
    parser.add_argument('-n','--n',type=int, help="Treshold for values or power if you use sqrt")
    return parser.parse_args()



def int_compression_function(file, N):
    job_file = file.split('.')[0] + '.sh'
    with open(job_file, 'w+') as fh:
        fh.writelines("#!/bin/sh\n")
        fh.writelines("#SBATCH --job=%s.job\n" % file.split('.')[0])
        fh.writelines("#SBATCH --partition=upex\n")
        fh.writelines("#SBATCH --time=12:00:00\n")
        fh.writelines("#SBATCH --nodes=1\n")
        fh.writelines("#SBATCH --mem=500000\n")
        fh.writelines("module load anaconda3/5.2\n")
        command = f'python3 /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/int_compression-upt.py {file} {path_to_data_cxi} {path_to_data} {N}'
        print(command)
        fh.writelines(command)
    os.system("sbatch %s" % job_file)


def int_compression_function_old(file, N):
    job_file = file.split('.')[0] + '.sh'
    with open(job_file, 'w+') as fh:
        fh.writelines("#!/bin/sh\n")
        fh.writelines("#SBATCH --job=%s.job\n" % file.split('.')[0])
        fh.writelines("#SBATCH --partition=upex\n")
        fh.writelines("#SBATCH --time=12:00:00\n")
        fh.writelines("#SBATCH --nodes=1\n")
        fh.writelines("#SBATCH --mem=500000\n")
        fh.writelines("module load anaconda3/5.2\n")
        command = f'python3 /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/int_compression.py {file} {path_to_data_cxi} {path_to_data} {N}'
        print(command)
        fh.writelines(command)
    os.system("sbatch %s" % job_file)

def sqrt_compression_function(file, N):
    job_file = file.split('.')[0] + '.sh'
    with open(job_file, 'w+') as fh:
        fh.writelines("#!/bin/sh\n")
        fh.writelines("#SBATCH --job=%s.job\n" % file.split('.')[0])
        fh.writelines("#SBATCH --partition=upex\n")
        fh.writelines("#SBATCH --time=60:00:00\n")
        fh.writelines("#SBATCH --nodes=1\n")
        fh.writelines("#SBATCH --mem=500000\n")
        fh.writelines("module load anaconda3/5.2\n")
        command = f'python3 /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/sqrt_compression_upt.py {file} {path_to_data_cxi} {path_to_data} {N}'
        print(command)
        fh.writelines(command)
    os.system("sbatch %s" % job_file)


def log_compression_function(file):
    job_file = file.split('.')[0] + '.sh'
    with open(job_file, 'w+') as fh:
        fh.writelines("#!/bin/sh\n")
        fh.writelines("#SBATCH --job=%s.job\n" % file.split('.')[0])
        fh.writelines("#SBATCH --partition=cfel\n")
        fh.writelines("#SBATCH --time=12:00:00\n")
        fh.writelines("#SBATCH --nodes=1\n")
        fh.writelines("#SBATCH --mem=500000\n")
        fh.writelines("module load anaconda3/5.2\n")
        command = f'python3 /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/log_compression.py {file} {path_to_data_cxi} {path_to_data}'
        fh.writelines(command)
    os.system("sbatch %s" % job_file)    


if __name__ == "__main__":
    args = parse_cmdline_args()
    path_from = args.p
    path_to_data_cxi = args.h5p
    path_to_data = args.h5pTo
    
    for path, dirs, all_files in os.walk(path_from):
        
        for cdir in dirs:
            path_from_dir = os.path.join(path, cdir)
            if 'S000' not in cdir:
                
                files = glob.glob(os.path.join(path_from_dir, '*.cxi'))
                if len(files) == 0:
                    files = glob.glob(os.path.join(path_from_dir, '*data*.h5'))
                
                if len(files) > 0:
                    #with Pool(processes=5) as pool:
                    #    pool.map(int_compression_function, files)
                    if args.old:
                        for file in files:
                            int_compression_function_old(file, args.n)                    
                    if args.intf:
                        for file in files:
                            int_compression_function(file, args.n)
                    if args.sqrt:
                        for file in files:
                            sqrt_compression_function(file, args.n)
                    if args.log:
                        for file in files:
                            log_compression_function(file)
                                               
        
            

