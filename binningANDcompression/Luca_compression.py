import glob
import os
import sys
from subprocess import call
from multiprocessing import Pool, TimeoutError

key="/entry/data/data"
chunks=(1, 4362, 4148)
compression="bzip2"
options=9
path_from = sys.argv[1]
path_to = sys.argv[2]

def gelisio_function(file):
    global key
    global chunks
    global compression
    global options
    dir_name = os.path.basename(os.path.dirname(file))
    output_dir = os.path.join(path_to, dir_name + '-compressed')
    
    if not(os.path.exists(output_dir)):
        #os.mkdir(output_dir)
        os.makedirs(output_dir, exist_ok=True)
    
    
    output_file = os.path.join(output_dir, os.path.basename(file))
    print(file + ' ---> ' + output_file)
    
    print('SBATCH PROCESS\n')
    
    job_file = output_file.split('.')[0] + '.job' #os.path.join(output_dir,"%s.job" % file.split('.')[0])
    
    with open(job_file, 'w+') as fh:
        fh.writelines("#!/bin/sh\n")
        fh.writelines("#SBATCH --job=%s.job\n" % file.split('.')[0])
        fh.writelines("#SBATCH --partition=upex\n")
        fh.writelines("#SBATCH --time=12:00:00\n")
        fh.writelines("#SBATCH --nodes=1\n")
        fh.writelines("#SBATCH --mem=500000\n")
        fh.writelines("load anaconda3/5.2\n")
        #command = 'python3.6 /asap3/petra3/gpfs/p11/2020/data/11010575/scratch_cc/gelisio/data-reduction/Eiger16M-compressor.py {} --key {} --output {} --chunks {} --compression {} --options {}'.format(file, key, output_file, chunks, compression, options)
        command = 'python3.6 /gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/Eiger16M-compressor.py {} --key {} --output {}\n'.format(file, key, output_file)
        fh.writelines(command)
    os.system("sbatch %s" % job_file)
    
    print('RUN %s' % job_file)
    
    
    




for path, dirs, all_files in os.walk(path_from):
        for dir in dirs:
            path_from_dir = os.path.join(path, dir)
            
            files = glob.glob(os.path.join(path_from_dir, '*data*.h5'))
            
            with Pool(processes=5) as pool:
                pool.map(gelisio_function, files)
        
            

