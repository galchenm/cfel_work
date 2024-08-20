import os
import sys
import subprocess
import re

file_with_files = sys.argv[1]
path_to_data_cxi = sys.argv[2]

total = 0
with open(file_with_files, 'r') as f:
    for file_cxi in f:
        if len(file_cxi) != 0:
            file_cxi = file_cxi.strip()
            data_dim = subprocess.check_output(['/opt/hdf5/hdf5-1.10.5/bin/h5ls', str(os.path.join(os.getcwd(),file_cxi))+str(path_to_data_cxi)])
            data_dim = data_dim.strip().decode('utf-8').split('Dataset ')[1]
            num = int(re.sub(r'({|}|/|Inf)','',data_dim).split(',')[0])
            total += num
            print(f"{os.path.basename(file_cxi)} - {num}")
            
print(f'Total patterns number is {total}')