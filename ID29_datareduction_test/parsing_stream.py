import os
import sys
import re
from collections import defaultdict

epsilon = 10e-1

def founded_peaks(stream):
    print('Start: Found peaks')
    data = defaultdict(dict)
    with open(stream, 'r') as file:
        
        in_list = 0
        for line in file:
            if line.startswith('Image filename:'):
                name_of_file = line.split()[-1]
                #print(name_of_file)
                continue
            if line.startswith('Event:'):
                event = line.split('//')[-1]
                if "{} //{}".format(name_of_file, event) not in data:
                    data["{} //{}".format(name_of_file, event)] = {}
                continue
            if line.find("Peaks from peak search") != -1: #Peaks from peak search
                in_list = 1
                continue
            if line.find("End of peak list") != -1: #End of peak list
                in_list = 0
            if in_list == 1:
                in_list = 2
                continue
            elif in_list != 2:
                continue

            # From here, we are definitely handling a reflection line

            # Add reflection to list
            columns = line.split() # fs/px   ss/px (1/d)/nm^-1   Intensity  Panel
            
            try:
                fs = float(columns[0])
                ss = float(columns[1])
                panel = columns[4]
                #print(f'panel = {panel}; fs = {fs}; ss = {ss}\n')
                key = "{} //{}".format(name_of_file, event)
                if panel not in data[key].keys():
                    data[key][panel] = []
                data[key][panel] += [(fs,ss),]    
            except:
                print("Error with line: "+line.rstrip("\r\n"))
    return data

def predicted_peaks(stream):
    print('Start: Predicted peaks')
    data = defaultdict(dict)
    with open(stream, 'r') as file:
        in_list = 0
        for line in file:
            if line.startswith('Image filename:'):
                name_of_file = line.split()[-1]
                #print(name_of_file)
                continue
            if line.startswith('Event:'):
                event = line.split('//')[-1]
                if "{} //{}".format(name_of_file, event) not in data:
                    data["{} //{}".format(name_of_file, event)] = {}
                continue
            if line.find("Reflections measured after indexing") != -1:
                in_list = 1
                continue
            if line.find("End of reflections") != -1:
                in_list = 0
            if in_list == 1:
                in_list = 2
                continue
            elif in_list != 2:
                continue

            # From here, we are definitely handling a reflection line

            # Add reflection to list
            #  h    k    l          I   sigma(I)       peak background  fs/px  ss/px panel
            columns = line.split()
            
            try:
                fs = float(columns[-3])
                ss = float(columns[-2])
                panel = columns[-1]
                #print(f'panel = {panel}; fs = {fs}; ss = {ss}\n')
                key = "{} //{}".format(name_of_file, event)
                if panel not in data[key].keys():
                    data[key][panel] = []
                data[key][panel] += [(fs,ss),] 
            except:
                print("Error with line: "+line.rstrip("\r\n"))
    return data  


def changes(stream, result):
   
    output_stream = os.path.join(os.path.dirname(stream),'reduced-' + os.path.basename(stream))
    print('Start: Changes')
    
    output = open(output_stream, 'w')
    with open(stream, 'r') as file:
        in_list = 0
        for line in file:
            if line.startswith('Image filename:'):
                name_of_file = line.split()[-1]
                output.write(line)
                #print(line , 1)
                continue
            if line.startswith('Event:'):
                #print(line , 2)
                output.write(line)
                event = line.split('//')[-1]
                continue
            if line.find("Reflections measured after indexing") != -1:
                output.write(line)
                in_list = 1
                #print(line , 3)
                continue
            if line.find("End of reflections") != -1:
                output.write(line)
                #print(line , 4)
                in_list = 0
            if in_list == 1:
                #print(line , 5)
                output.write(line)
                in_list = 2
                #continue
                
            elif in_list != 2:
                #print(line , 6)
                output.write(line)
                print(line)
                continue

            # From here, we are definitely handling a reflection line

            # Add reflection to list
            #  h    k    l          I   sigma(I)       peak background  fs/px  ss/px panel
            columns = line.split()
            #print(columns)
            try:
                fs = float(columns[-3])
                ss = float(columns[-2])
                panel = columns[-1]
                #print(f'panel = {panel}; fs = {fs}; ss = {ss}\n')
                key = "{} //{}".format(name_of_file, event)
                if key in result.keys() and panel in result[key].keys() and (fs,ss) in result[key][panel]:
                    #              h  k   l     I   sigma(I)    peak background  fs/px  ss/px panel
                    print('HERE')
                    new_line =  "%4i %4i %4i %10.2f %10.2f %10.2f %10.2f %6.1f %6.1f %s\n"%(int(columns[0]), int(columns[1]), int(columns[2]), 0.0, 0.0, float(columns[5]), float(columns[6]), fs, ss, panel)
                    #print(new_line)
                    output.write(new_line)
                
                else:
                    print(line)
                    output.write(line)
                    
                   
            except:
                print("Error with line: "+line.rstrip("\r\n"))
    output.close()
    
stream = sys.argv[1]

dict_founded_peaks = founded_peaks(stream)
print('End: Found peaks')
dict_predicted_peaks = predicted_peaks(stream)
print('End: Predicted peaks')

dict_founded_peaks_wo_empty = {k:v for k,v in dict_founded_peaks.items() if v}
dict_predicted_peaks_wo_empty = {k:v for k,v in dict_predicted_peaks.items() if v}

print('Sorted dictionaries')
#print(dict_founded_peaks_wo_empty)
#print(dict_predicted_peaks_wo_empty)
print()
print()

print('Start finding results')

result = {}
for key in dict_predicted_peaks_wo_empty:
    result[key] = {}
    for panel in dict_predicted_peaks_wo_empty[key]:#
        panels_from_founded_peaks = list(dict_founded_peaks_wo_empty[key].keys())
        
        if panel not in panels_from_founded_peaks:
            print(f'This {panel} is absent in founded peaks')
            #result[key] = {k: v for k,v in dict_predicted_peaks_wo_empty[key].items()}
            result[key][panel] = dict_predicted_peaks_wo_empty[key][panel]
        else:
            print(f'This is {panel}')
            
            fs_ss_predicted_peaks = dict_predicted_peaks_wo_empty[key][panel]
            fs_ss_founded_peaks = dict_founded_peaks_wo_empty[key][panel]
            
            fs_ss_founded_peaks.sort()
            fs_ss_predicted_peaks.sort()
            
            print(f'fs_ss_predicted_peaks = {fs_ss_predicted_peaks}')
            print(f'fs_ss_founded_peaks = {fs_ss_founded_peaks}')
            
            dd = []
            
            for pair in fs_ss_predicted_peaks:
                print(f'predicted pair is {pair}')
                delta = [(i[0] - pair[0])**2+ (i[1] - pair[1]) ** 2 for i in fs_ss_founded_peaks] # if (i[0] - pair[0])**2+ (i[1] - pair[1]) ** 2 > epsilon
                print(f'delta = {delta}')
                dd += [pair for i in fs_ss_founded_peaks if (i[0] - pair[0])**2+ (i[1] - pair[1]) ** 2 < epsilon]
                print(f'dd = {dd}')
                
            print(f'final dd = {dd}')
            need_to_add = list(set(fs_ss_predicted_peaks) - set(dd))
            print(f'what we need to add to result is {need_to_add}')
            if len(need_to_add) > 0:
                result[key][panel] = need_to_add
                print(f'result[{key}][{panel}] = {result[key][panel]}')
        print(f'result[{key}]= {result[key]}')
     
#print(dict_predicted_peaks_wo_empty["{} //{}".format('/gpfs/exfel/u/scratch/SPB/202002/p002442/cheetah/hdf5/r0107-cry60a_dark58/EuXFEL-S00000-r0107-c00.cxi', '30\n')]['p4a5'])
#print(dict_founded_peaks_wo_empty ["{} //{}".format('/gpfs/exfel/u/scratch/SPB/202002/p002442/cheetah/hdf5/r0107-cry60a_dark58/EuXFEL-S00000-r0107-c00.cxi', '30\n')]['p4a5'])
#print(result)
#print(result["{} //{}".format('/gpfs/exfel/u/scratch/SPB/202002/p002442/cheetah/hdf5/r0107-cry60a_dark58/EuXFEL-S00000-r0107-c00.cxi', '30\n')]['p4a5'])
changes(stream, result)