#!/usr/bin/env python3
# Geometry converter from Cheetah to proc format and vice versa
# python3 GeometryConverter.py <mode> <in_geom> <out_geom> <path to data>
# mode = 1 - convert from Cheetah to proc
# mode = 2 - convert from proc to Cheetah
# Ex., path to data = /entry_1/instrument_1/detector_1/data


import sys
import os
from datetime import date

os.nice(0)


if __name__ == "__main__":
    
    print('It is a geometry converter\n')
    n = int(sys.argv[1]) # mode of the converter
    in_geom_file_name = sys.argv[2]
    out_geom_file_name = sys.argv[3]

    in_geom = open(in_geom_file_name, 'r')  # from
    out_geom = open(out_geom_file_name, 'w') # to
    path_to_data = sys.argv[4]
    today = date.today()
    out_geom.write('; This geometry file {} was made from {}, {}\n'.format(out_geom_file_name, in_geom_file_name,today.strftime("%d-%b-%Y")))

    if n == 1: # convert from Cheetah to proc
        print('From Cheetah format to proc format\n')
        print('Start the process of converting\n')
        panels = []
        bad_panels = []
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
                    if 'bad' in line:
                        l = line.split('/')
                        # print(l[0])
                        if l[0] not in bad_panels:
                            # print(l[0])
                            bad_panels.append(l[0])
                            num_panel = (s[0].split('/')[0]).split('p')[1]
                            out_geom.write(l[0]+'/dim1 = '+num_panel+'\n')
                            out_geom.write(l[0]+'/dim2 = ss \n')
                            out_geom.write(l[0]+'/dim3 = fs \n')
                            # print(bad_panels)
                else:
                    out_geom.write(line)

        out_geom.write('\n')
        out_geom.write('\n')
        for i in panels:
            line = i+'/dim1 = '+ (i.split('a')[0]).split('p')[1]
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
                pass
            else:
                s = line.split(' = ')[0].split('/')
                if len(s) == 2 and s[1] in ('min_ss', 'max_ss'):
                    s = line.split(' = ')
                    if len(s) == 2:
                        if ((s[0].split('/')[0]).split('p')[1]).isdigit():
                            num_panel = int((s[0].split('/')[0]).split('p')[1])
                        else:
                            num_panel = int(((s[0].split('/')[0]).split('a')[0]).split('p')[-1])
                        v = int(s[1]) + num_panel * 512 # or (num_panel -1)*512+ss
                        num_panel += 1 
                        out_geom.write('%s = %d\n'%(s[0], v))
                else:
                    out_geom.write(line)

        in_geom.close()
        out_geom.close()
        print('Finish the process of converting\n')