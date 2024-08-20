#!/usr/bin/env python3
# coding: utf8


import os
import sys
import subprocess
import re
import glob
from multiprocessing import Pool, TimeoutError
import logging
import shutil

def rm_files_and_empty_dirs(root):
    global logger
    
    data_files=glob.glob(os.path.join(root,'*_data*.h5'))
    if len(data_files) > 0: 
        for file in data_files:
            try:
                data_dim = subprocess.check_output(['/opt/hdf5/hdf5-1.10.5/bin/h5ls', file +'/entry/data'])
                data_dim = data_dim.strip().decode('utf-8').split('Dataset ')[1]
                num = int(re.sub(r'({|})','',data_dim).split('/')[0])
                if num == 0:
                    print(file + ' empty\n')
                    logger.warning('The file {} is empty.\n'.format(os.path.basename(file)))
                    os.remove(file)
            except subprocess.CalledProcessError as e:
                logger.error('Impossible to open file {}.\n'.format(os.path.basename(file)))
                print(os.path.basename(file) + ' ERROR\n')
    
    if len(glob.glob(os.path.join(root,'*_data*.h5'))) == 0:
        logger.warning('The folder {} is empty.\n'.format(root))
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":

    input_path = sys.argv[1]
    folders = [x[0] for x in os.walk(input_path) if x[0] != input_path]
    

    logger = logging.getLogger(__name__)
    f_handler = logging.FileHandler(os.path.join(input_path, 'file.log'))
    
    f_format = logging.Formatter('%(levelname)s - %(message)s')
    f_handler.setFormatter(f_format)
    logger.addHandler(f_handler)

    with Pool(processes=len(folders)) as pool:
        pool.map(rm_files_and_empty_dirs, folders)