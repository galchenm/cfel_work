import os
import pyinotify
import sys
import h5py as h5
import numpy as np
import glob
import subprocess
import time
import re

#dir_name = '/asap3/petra3/gpfs/p11/2022/data/11013278/scratch_cc/galchenm/test_chip_dozor' #TO CHANGE

MIN_NUM_PEAKS = 30

hdf5path = '/entry/data/data'


def parsing_dozor(file):
    global dir_name
    print(file)
    NumOFline = re.search(r'\d+\.out',os.path.basename(file)).group().split('.')[0]
    number_for_hdf5_file = NumOFline.zfill(6)
    output = os.path.join(dir_name, os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(file)))) + '_' + os.path.basename(os.path.dirname(os.path.dirname(file))))
    
    if not(os.path.exists(output)):
        os.mkdir(output)
    output_filename = os.path.join(output, NumOFline+'.lst')
    print(output_filename)
        
    with open(file, 'r') as f:
        start = 0
        for line in f:
             
            if '+ image_data_filename   =' in line:
                #+ image_data_filename   = </asap3/petra3/gpfs/p11/2022/data/11013662/raw/lyso_new_1/grid_001/lyso_new_1_grid_001_master.h5  >
                image_filename = line.split(' = ')[1].replace('<','').replace('>','').strip()
                image_data_filename = image_filename.replace('master',f'data_{number_for_hdf5_file}')
                h5file = h5.File(image_data_filename, 'r')
                num = h5file[hdf5path].shape[0]
                h5file.close()
                print(image_data_filename)
                continue
            elif 'image | num.of   Score    Resolution' in line:
                start = 1
                continue
            elif start == 1:
                
                start = 2
                continue
            elif start != 2:
                continue
                
            elif '------------------------------------' in line and start == 2:
                break
            
            tmp = re.search(r'\d+ \|[^\S\n\t]+\d+', line).group()
            number_of_pattern, num_peaks = tmp.split('|')
            number_of_pattern = int(number_of_pattern.strip())
            num_peaks = int(num_peaks.strip())
            print('NUM PEAKS = ', num_peaks)
            if num_peaks > MIN_NUM_PEAKS:
                if os.path.exists(output_filename):
                    append_write = 'a' # append if already exists
                else:
                    append_write = 'w' # make a new file if not
                #print(number_of_pattern, NumOFline, number_of_pattern - ((int(NumOFline)-1)*num))
                imageNumber = number_of_pattern - ((int(NumOFline)-1)*num)
                out = open(output_filename, append_write)
                #out.write(f'{imageNumber -1},{int(NumOFline)-1}\n')
                out.write(f'{imageNumber},{int(NumOFline)-1}\n')
                out.close()
def Monitor(path):
    
    list_of_files = glob.glob(f'{path}/dozor/dozorr*out')
    print(list_of_files)
    processed = []
    after = len(list_of_files)
    while(after == 0):
        list_of_files =  glob.glob(f'{path}/dozor/dozorr*out')
        after = len(list_of_files)
        
    #while(1):
    for file in list_of_files:
        if file not in processed:
            processed.append(file)
            #print(file)
            #calling_peakfinder8(file)
            parsing_dozor(file)
    #time.sleep(2.5)
    list_of_files =  glob.glob(f'{path}/dozor/dozorr*out')

    
if __name__ == '__main__':
    path = sys.argv[1]
    dir_name = sys.argv[2]
    while 1:
        #print(1)
        if os.path.exists(path):
            print('appeared')
            
            break
    Monitor(path)
