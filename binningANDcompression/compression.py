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
        os.mkdir(output_dir)
    
    output_file = os.path.join(output_dir, os.path.basename(file))
    print(file + ' ---> ' + output_file)
    #command = 'python3.6 /asap3/petra3/gpfs/p11/2020/data/11010575/scratch_cc/gelisio/data-reduction/Eiger16M-compressor.py {} --key {} --output {} --chunks {} --compression {} --options {}'.format(file, key, output_file, chunks, compression, options)
    command = 'python3.6 /asap3/petra3/gpfs/p11/2020/data/11010575/scratch_cc/gelisio/data-reduction/Eiger16M-compressor.py {} --key {} --output {}'.format(file, key, output_file)
   
    os.system(command)
    #print(command)
    
    
    




for path, dirs, all_files in os.walk(path_from):
        for dir in dirs:
            path_from_dir = os.path.join(path, dir)
            
            files = glob.glob(os.path.join(path_from_dir, '*data*.h5'))
            
            with Pool(processes=5) as pool:
                pool.map(gelisio_function, files)
        
            

