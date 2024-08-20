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

import argparse

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-f','--f', type=str, help='File with blocks')
    parser.add_argument('-i', type=str, help="Input dir with raw file")
    parser.add_argument('-o', type=str, help="Output dir where to save result")
    parser.add_argument('-d', type=str, help="Input dir with dark files")
    return parser.parse_args()

def processing(path):
    if 'darks' not in path and 'todel' not in path:
        h5files = glob.glob(os.path.join(path, '*.h5'))
        if len(h5files) > 0:
            print(path)
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

            template_data = {"OUTPUT": new_output_path,"RUN": new_output_name, "DARKd0" : dark_d0, "DARKd1" : dark_d1 }
            monitor_file = open('monitor.yaml', 'w')
            with open('template.yaml', 'r') as f:
                src = Template(f.read())
                result = src.substitute(template_data)
                monitor_file.write(result)
            monitor_file.close()
            os.remove('template.yaml')
            
            command = f'source /gpfs/cfel/group/cxi/scratch/data/2021/ESRF-2021-Meents-Oct-ID09/scratch/galchenm/run_cheetah.sh {path} {new_output_name} {new_output_path}'
            
            os.system(command)
            
args = parse_cmdline_args()
path_input = args.i
path_subpanels_darks = args.d
output = args.o

to_be_processed = []
if args.f is not None:
    with open(args.f, 'r') as f:
        for line in f:
            to_be_processed += [line.strip()]

#print(to_be_processed)

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
    

for path, dirs, all_files in os.walk(path_input):
    if len(to_be_processed) > 0 and bool([ele for ele in to_be_processed if(ele in path)]):
        processing(path)
    if len(to_be_processed) == 0:
        processing(path)    

command = f'chmod 777 -R {output}'
os.system(command)          