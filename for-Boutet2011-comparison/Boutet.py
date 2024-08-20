#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import h5py as h5
import os
import sys

from collections import defaultdict
import pandas as pd

first_list_of_files = sys.argv[1]
h5path_machineTime1 = sys.argv[2]
h5path_fiducial1 = sys.argv[3]
dd_1 = defaultdict(list)


second_list_of_files = sys.argv[4]
h5path_machineTime2 = sys.argv[5]
h5path_fiducial2 = sys.argv[6]
dd_2 = defaultdict(list)

filename = None
event = None
machineTime = None
fiducial = None


with open(first_list_of_files, 'r') as file:
    for line in file:
        filename, event = line.split(' ')
        dd_1['filename'].append(filename)
        dd_1['event'].append(event)
        link_to_data = h5.File(filename.strip(), 'r')
        machineTime = link_to_data[h5path_machineTime1][int(event.replace('//',''))]
        fiducial = link_to_data[h5path_fiducial1][int(event.replace('//',''))]
        dd_1['machineTime'].append(machineTime)
        dd_1['fiducial'].append(fiducial)
        print('{}\t{}\t{}\t{}\n'.format(filename, event, machineTime, fiducial))

df = pd.DataFrame(dd_1)
csv_name = '1.csv'
df.to_csv( csv_name, index = False, header=True, sep='\t')

print('Second')

with open(second_list_of_files, 'r') as file:
    for line in file:
        filename, event = line.split(' ')
        dd_2['filename'].append(filename)
        dd_2['event'].append(event)
        link_to_data = h5.File(filename.strip(), 'r')
        machineTime = link_to_data[h5path_machineTime2][int(event.replace('//',''))]
        fiducial = link_to_data[h5path_fiducial2][int(event.replace('//',''))]
        dd_2['machineTime'].append(machineTime)
        dd_2['fiducial'].append(fiducial)
        print('{}\t{}\t{}\t{}\n'.format(filename, event, machineTime, fiducial))

df2 = pd.DataFrame(dd_2)
csv_name = '2.csv'
df2.to_csv(csv_name, index = False, header=True, sep='\t')


print('Find intersection and differance between indexed patterns\n')
mergedStuff = pd.merge(df, df2, on=['machineTime', 'fiducial'], how='inner', suffixes=('_fisrt', '_second')) #intersection
diffferentStuff =  pd.concat([df,df2]).drop_duplicates(subset=['machineTime', 'fiducial'], keep=False) #differance

print('Saving results into csv\n')
mergedStuff.to_csv('result_intersection.csv', index = False, header=True, sep='\t')
diffferentStuff.to_csv('result_diff.csv', index = False, header=True, sep='\t')
