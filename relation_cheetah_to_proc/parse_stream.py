#!/usr/bin/env python3

"""
python3 parse_stream.py proc_r0095.stream cheetah_r0095.stream
Input: 2 streams
Output: parsing each streams, their intersection and difference 
"""


import os
import sys
import h5py as h5
import subprocess
import re
import argparse
from collections import defaultdict
import pandas as pd


class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('first_stream', type=str, help="First input stream file")
    parser.add_argument('second_stream', type=str, help="Second input stream file")
    return parser.parse_args()

def get_opt_patterns(stream_name):
    dd_f = defaultdict(list)
    with open(stream_name, 'r') as stream:
        name_of_file = None
        serial_number = None
        method_index = None
        pulseId = None
        trainId = None
        num_peaks = None

        for line in stream:
            if line.startswith('Image filename:'):
                # Image filename: /gpfs/exfel/u/scratch/SPB/202001/p002450/yefanov/cheetah-lyso/hdf5/r0095-lyso_dk109/EuXFEL-S00000-r0095-c00.cxi
                name_of_file = line.split()[-1] 
                
            if line.startswith('Event:'):
                # Image serial number: 1789
                serial_number = line.split('//')[-1] 
                
            if line.startswith('indexed_by ='): #none
                # indexed_by = none
                method_index = line.split()[-1] 
                

            if any(call_id in line for call_id in ['pulseId', 'pulseID']):
                # hdf5/entry_1/pulseId = 496
                pulseId = line.split()[-1]   

            if any(call_id in line for call_id in ['trainId', 'trainID']):
                #hdf5/entry_1\trainId = 496
                trainId = line.split()[-1]
                
            if line.startswith('num_peaks ='):
                # num_peaks = 35
                num_peaks = line.split()[-1]
                
            if (name_of_file is not None) and (serial_number is not None) and (method_index is not None) and (pulseId is not None) and (trainId is not None) and (num_peaks is not None):
                if 'none' not in method_index:
                    dd_f['file_name'].append(name_of_file)
                    dd_f['event_number'].append(int(serial_number))
                    dd_f['indexed_by'].append(method_index)
                    dd_f['pulse_ID'].append(int(pulseId))
                    dd_f['train_ID'].append(int(trainId))
                    dd_f['num_peaks'].append(int(num_peaks))

                #print('{}\t{}\t{}\t{}\t{}\t{}\n'.format(name_of_file, serial_number, method_index, pulseId, trainId, num_peaks))
                name_of_file = None
                serial_number = None
                method_index = None
                pulseId = None
                trainId = None
                num_peaks = None
    df = pd.DataFrame(dd_f)
    
    csv_name = os.path.basename(stream_name).split('.')[0] + '_parse.csv'
    
    df.to_csv(os.path.join(os.getcwd(), csv_name), index = False, header=True, sep='\t')

    return df

if __name__ == "__main__":
    args = parse_cmdline_args()
    stream_name_1 = args.first_stream
    stream_name_2 = args.second_stream
    print('Get patterns from stream\n')
    df1 = get_opt_patterns(stream_name_1) # vds
    df2 = get_opt_patterns(stream_name_2) # no_vds

    print('Find intersection and differance between indexed patterns\n')
    mergedStuff = pd.merge(df1, df2, on=['train_ID', 'pulse_ID'], how='inner', suffixes=('_proc', '_cheetah')) #intersection
    diffferentStuff =  pd.concat([df1,df2]).drop_duplicates(subset=['train_ID', 'pulse_ID'], keep=False) #differance

    print('Saving results into csv\n')
    mergedStuff.to_csv(os.path.join(os.getcwd(), 'result_intersection.csv'), index = False, header=True, sep='\t')
    diffferentStuff.to_csv(os.path.join(os.getcwd(), 'result_diff.csv'), index = False, header=True, sep='\t')

    