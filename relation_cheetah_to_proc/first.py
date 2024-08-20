#!/usr/bin/env python
# coding: utf8

"""
python3 first.py [name_of_stream]

python3 first.py proc_r0095.stream

Input: stream file with all patterns
Ouput: csv file with name of file, pulse/train ID, event number, menInt, number of peaks
"""
import sys
import numpy as np
import h5py
import os
from os.path import basename, splitext
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
    parser.add_argument('stream', type=str, help="Input stream file")
    return parser.parse_args()


def getting_mean_intensity(name_of_stream_file):
    dd_f = defaultdict(list)
    with open(name_of_stream_file, 'r') as stream:
        
        reading_chunks = False
        reading_peaks = False

        name_of_file = None
        serial_number = None
        method_index = None
        pulseId = None
        trainId = None
        num_peaks = None
        mean_Int = None

        for line in stream:

            if line.startswith('----- Begin chunk -----'):
                reading_chunks = True

            elif reading_chunks:
                if line.startswith('Image filename:'):
                    name_of_file = line.split()[-1] 
                    
                elif line.startswith('Event:'):
                    serial_number = line.split('//')[-1] 
                    
                elif line.startswith('indexed_by ='): 
                    method_index = line.split()[-1] 
                    
                elif any(call_id in line for call_id in ['pulseId', 'pulseID']):
                    pulseId = line.split()[-1]   

                elif any(call_id in line for call_id in ['trainId', 'trainID']):
                    trainId = line.split()[-1]
                    
                elif line.startswith('num_peaks ='):
                    num_peaks = line.split()[-1]

                elif line.startswith('End of peak list'):
                    reading_peaks = False
                    end_of_reading_peaks = True
                    if numInt != 0:
                        mean_Int = round(sumInt/numInt,2)

                elif line.startswith('  fs/px   ss/px (1/d)/nm^-1   Intensity  Panel'):
                    reading_peaks = True
                    sumInt = 0
                    numInt = 0
                elif reading_peaks:
                    fs, ss, dump, intensity = [float(i) for i in line.split()[:4]]
                    
                    sumInt += intensity
                    numInt += 1

                elif line.strip() == '----- End chunk -----':
                    reading_chunk = False

                    if (name_of_file is not None) and (serial_number is not None) and (method_index is not None) and (pulseId is not None) and (trainId is not None) and (num_peaks is not None) and (mean_Int is not None):
                        if 'none' not in method_index:
                            dd_f['file_name'].append(name_of_file)
                            dd_f['event_number'].append(int(serial_number))
                            dd_f['indexed_by'].append(method_index)
                            dd_f['pulse_ID'].append(int(pulseId))
                            dd_f['train_ID'].append(int(trainId))
                            dd_f['num_peaks'].append(int(num_peaks))
                            dd_f['mean_Int'].append(mean_Int)

                        print('{}\t{}\t{}\t{}\t{}\n'.format(name_of_file, serial_number, pulseId, trainId, mean_Int))

                        name_of_file = None
                        serial_number = None
                        method_index = None
                        pulseId = None
                        trainId = None
                        num_peaks = None
                        mean_Int = None

    df = pd.DataFrame(dd_f)
    csv_name = stream_name.split('.')[0] + '_mean_Int.csv'
    df.to_csv(os.path.join(os.getcwd(), csv_name), index = False, header=True, sep='\t')

    return df

if __name__ == "__main__":
    args = parse_cmdline_args()
    stream_name = args.stream
    df = getting_mean_intensity(stream_name)
    print(round(df['mean_Int'].mean(), 2))