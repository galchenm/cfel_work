import os
import sys
import glob
import subprocess
import shlex
import re
from collections import defaultdict
import time
import datetime
from string import Template

path_input = sys.argv[1]
path_subpanels_darks = sys.argv[2]
output = sys.argv[3]

d_darks = defaultdict(dict)
list_of_files_d = glob.glob(os.path.join(path_subpanels_darks, '*d0_*.h5'))


for file in list_of_files_d:
    name = os.path.basename(file)
    name = name.split('_f')[0]
    command_line = f'ls {file} -lh'
    result = subprocess.check_output(shlex.split(command_line)).decode('utf-8').strip().split('\n')
    result.sort()
    rights, n, owner, group, Volume, Month, Date, Time, name_tmp = result[0].split()
    
    x = time.strptime(f'{Date} {Month} {Time}', "%d %b %H:%M")
    d_darks[name] = datetime.timedelta(days=x.tm_yday, hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
    
#print(d_darks)   

for path, dirs, all_files in os.walk(path_input):
    if 'darks' not in path and 'todel' not in path:
        h5files = glob.glob(os.path.join(path, '*.h5'))
        if len(h5files) > 0:
            
            command_line = f'ls {path}/ -lh'
            result = subprocess.check_output(shlex.split(command_line)).decode('utf-8').strip().split('\n')
            result.sort()

            #'-rw-rw-rw-', '1', 'yefanov', 'cfel', '16K', 'Oct', '27', '22:22', 'run0002_master_1.h5']
            rights, n, owner, group, Volume, Month, Date, Time, name = result[0].split()
            x = time.strptime(f'{Date} {Month} {Time}', "%d %b %H:%M")
            total_second_for_file = datetime.timedelta(days=x.tm_yday, hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds() 
            
            dark_for_run = ''
            min_delta_time = 10e60
            for key in d_darks:
                if abs(total_second_for_file - d_darks[key]):
                    dark_for_run = key
                    min_delta_time = abs(total_second_for_file - d_darks[key])
            
            new_output_name = f'{os.path.basename(os.path.dirname(path))}_{os.path.basename(path)}'
            
            new_output_path = os.path.join(output, new_output_name)
            if not(os.path.exists(new_output_path)):
                os.mkdir(new_output_path)
            os.chdir(new_output_path)
            command = "cp /gpfs/cfel/group/cxi/scratch/data/2021/ESRF-2021-Meents-Oct-ID09/scratch/galchenm/template.yaml ."
            os.system(command)

            dark_d0 = os.path.join(path_subpanels_darks, f'{dark_for_run}.h5')

            dark_d1 = os.path.join(path_subpanels_darks, f'{dark_for_run.replace("_d0","_d1")}.h5')
            #print(dark_d0)
            

            template_data = {"OUTPUT": new_output_path,"RUN": new_output_name, "DARKd0" : dark_d0, "DARKd1" : dark_d1 }
            monitor_file = open('monitor.yaml', 'w')
            with open('template.yaml', 'r') as f:
                src = Template(f.read())
                result = src.substitute(template_data)
                monitor_file.write(result)
            monitor_file.close()
            os.remove('template.yaml')
            
            command = f'source /gpfs/cfel/group/cxi/scratch/data/2021/ESRF-2021-Meents-Oct-ID09/scratch/galchenm/run_cheetah.sh {path} {new_output_name} {new_output_path}'
            #print(command)
            os.system(command)
            
        
        