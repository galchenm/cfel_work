import glob
import os
import sys
from subprocess import call
from multiprocessing import Pool, TimeoutError


path_from = sys.argv[1]
path_to = sys.argv[2]

def tolstikova_function(run):
    output_dir = os.path.join(path_to, run + '-compressed')
    
    command = 'source /gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/run_cheetah_compression.sh {} {}'.format(run, output_dir)
    #print(command)
    os.system(command)
    
    
    
    




for path, dirs, all_files in os.walk(path_from):
    runs = [os.path.basename(dir) for dir in dirs]
    with Pool(processes=5) as pool:
        pool.map(tolstikova_function, runs)
        
            

