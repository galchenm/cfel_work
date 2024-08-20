import os
import sys
import subprocess
import re
import glob

f = '/asap3/petra3/gpfs/p11/2020/data/11010575/scratch_cc/galchenm/compression_comparison/with_v0_mask' #'/asap3/petra3/gpfs/p11/2020/data/11010575/scratch_cc/galchenm/compression/'
l = '/asap3/petra3/gpfs/p11/2020/data/11010575/scratch_cc/galchenm/compression_comparison/with_v0_mask/lists' #'/asap3/petra3/gpfs/p11/2020/data/11010575/scratch_cc/galchenm/compression-analys/lists'

for root,dirs, files in os.walk(f):
    lines=glob.glob(os.path.join(root,'*_data*.h5'))
    if len(lines) > 0:
        with open(os.path.join(l,os.path.basename(root).split('-')[0]+'.lst'),'w') as w:
            for line in lines:
                #data_dim = subprocess.check_output(['/opt/hdf5/hdf5-1.10.5/bin/h5ls', line +'/entry/data'])
                try:
                    data_dim = subprocess.check_output(['/opt/hdf5/hdf5-1.10.5/bin/h5ls', line +'/entry/data'])
                    data_dim = data_dim.strip().decode('utf-8').split('Dataset ')[1]
                    num = int(re.sub(r'({|})','',data_dim).split('/')[0])
                    
                    if num > 0:
                        w.write(line+'\n')
                    else:
                        print(os.path.basename(line) + ' empty\n')
                except subprocess.CalledProcessError as e:
                    print(os.path.basename(line) + ' ERROR\n')
