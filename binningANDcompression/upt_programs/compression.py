import glob
import os
import sys
from subprocess import call
from multiprocessing import Pool, TimeoutError


path_from = sys.argv[1]


def int_compression_function(file):
    job_file = file.split('.')[0] + '.job'
    with open(job_file, 'w+') as fh:
        fh.writelines("#!/bin/sh\n")
        fh.writelines("#SBATCH --job=%s.job\n" % file.split('.')[0])
        fh.writelines("#SBATCH --partition=upex\n")
        fh.writelines("#SBATCH --time=12:00:00\n")
        fh.writelines("#SBATCH --nodes=1\n")
        fh.writelines("#SBATCH --mem=500000\n")
        fh.writelines("module load anaconda3/5.2\n")
        command = 'python3 /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/int_compression.py {}'.format(file)
        fh.writelines(command)
    os.system("sbatch %s" % job_file)
    

    

for path, dirs, all_files in os.walk(path_from):
    
    for dir in dirs:
        path_from_dir = os.path.join(path, dir)
        if 'S000' not in dir:
            
            files = glob.glob(os.path.join(path_from_dir, '*.cxi'))
            
            if len(files) > 0:
                for file in files:
                    print(file)
                    int_compression_function(file)
                #with Pool(processes=5) as pool:
                #    pool.map(int_compression_function, files)
        
            

