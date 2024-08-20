#!/usr/bin/env python3

"""
Geometry converter from Cheetah to proc format and vice versa
python3 GeometryConverter.py <mode> <in_geom> <out_geom> <path to data>
mode = 1 - convert from Cheetah to proc
mode = 2 - convert from proc to Cheetah
Ex., path to data = /entry_1/instrument_1/detector_1/data
"""

import sys
import os
from datetime import date
import argparse
import re

os.nice(0)

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('mode', type=int, help="Mode of converter: from cheetah to proc or vice versa")
    parser.add_argument('input_geom', type=str, help="Input geometry file")
    parser.add_argument('output_geom', type=str, help="Output geometry file")
    parser.add_argument('path', type=str, help="The hdf5 path to data")
    return parser.parse_args()

if __name__ == "__main__":
    print('It is a geometry converter\n')
    args = parse_cmdline_args()

    
    n = args.mode # mode of the converter
    in_geom_file_name = args.input_geom
    out_geom_file_name = args.output_geom
    path_to_data = args.path

    in_geom = open(in_geom_file_name, 'r')  # from
    out_geom = open(out_geom_file_name, 'w') # to
    
    today = date.today()
    out_geom.write('; This geometry file {} was made from {}, {}\n'.format(out_geom_file_name, in_geom_file_name,today.strftime("%d-%b-%Y")))
    d_for_non_vds = {'dim1':'', 'dim2':''}
    correlation = {'dim1': 'dim0', 'dim2': 'dim1', 'dim3': 'dim2'}
    if n == 1: # convert from Cheetah to proc
        print('From Cheetah format to proc format\n')
        print('Start the process of converting\n')
        panels = []
        for line in in_geom:
            if line.startswith('dim1 ') and not(line.startswith(';')):
                line = ';dim2 = '+line.split(' = ')[1]
                out_geom.write(line)
            elif line.startswith('dim2 ') and not(line.startswith(';')):
                line = ';dim3 = '+line.split(' = ')[1]
                out_geom.write(line)
            elif line.startswith('data =') and not(line.startswith(';')):
                line = 'data = '+path_to_data+'\n'
                out_geom.write(line)
            else:
                s = line.split(' = ')[0].split('/')
                if len(s) == 2 and s[1] in ('min_ss', 'max_ss'):
                    if s[0] not in panels and not(line.startswith(';')):
                        panels.append(s[0])
                    s = line.split(' = ')
                    if len(s) == 2:
                        v = int(s[1]) % 512
                        out_geom.write('%s = %d\n'%(s[0], v))
                            
                else:
                    out_geom.write(line)

        out_geom.write('\n')
        out_geom.write('\n')
        
        for i in panels:
            line = i+'/dim1 = '+ re.findall(r'[\d\.]+', i)[0]
            out_geom.write(line+'\n')

        out_geom.write('\n')
        out_geom.write('\n')
        for i in panels:
            line = i+'/dim2 = ss'
            out_geom.write(line+'\n')
        
        out_geom.write('\n')
        out_geom.write('\n')
        for i in panels:
            line = i+'/dim3 = fs'
            out_geom.write(line+'\n')
        
        in_geom.close()
        out_geom.close()
        print('Finish the process of converting\n')

    else:
        print('From proc format to Cheetah format\n')
        print('Start the process of converting\n')

        check_list = ['/dim1','/dim2','/dim3']
        for line in in_geom:
            if line.startswith(';dim2 '):
                line = 'dim1 = '+line.split(' = ')[1]
                out_geom.write(line)
            elif line.startswith(';dim3 '):
                line = 'dim2 = '+line.split(' = ')[1]
                out_geom.write(line)
            elif line.startswith('data =') and not(line.startswith(';')):
                line = 'data = '+path_to_data+'\n'
                out_geom.write(line)
            elif any(item in line for item in check_list): 
                # '/dim1' in line or '/dim2' in line or '/dim3' in line
                
                if ('dim2' in line or 'dim3' in line) and not(line.startswith(';')):
                    #print(line)
                    prefix, ss_fs = line.strip().split(' = ')
                    dim = prefix.split('/')[-1]
                    #print(dim, ss_fs, correlation[dim])
                    d_for_non_vds[correlation[dim]] = ss_fs
            else:
                s = line.split(' = ')[0].split('/')
                if len(s) == 2 and s[1] in ('min_ss', 'max_ss'):
                    s = line.split(' = ')
                    if len(s) == 2:
                        num_panel = int(re.findall(r'[\d\.]+', s[0])[0])
                        print(num_panel)
                        v = int(s[1]) + num_panel * 512 # or (num_panel -1)*512+ss
                        # num_panel += 1 
                        out_geom.write('%s = %d\n'%(s[0], v))
                else:
                    out_geom.write(line)
        print(d_for_non_vds)
        for key in d_for_non_vds:
            out_geom.write(f"{key} = {d_for_non_vds[key]}\n")
        in_geom.close()
        out_geom.close()
        print('Finish the process of converting\n')