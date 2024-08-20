#!/usr/bin/env python3
# coding: utf8


import os
import sys


import numpy as np
import pandas as pd


def get_xy(file_name, x_arg_name, y_arg_name):
    x = []
    y = []

    with open(file_name, 'r') as stream:
        for line in stream:
            if y_arg_name in line:
                tmp = line.replace('1/nm', '').replace('# ', '').replace('centre', '').replace('/ A', '').replace(' dev','').replace('(A)','')
                tmp = tmp.split()
                y_index = tmp.index(y_arg_name)
                x_index = tmp.index(x_arg_name)

            else:
                tmp = line.split()
                
                x.append(float(tmp[x_index]) if not np.isnan(float(tmp[x_index])) else 0. )
                y.append(float(tmp[y_index]) if not np.isnan(float(tmp[y_index])) else 0. )

    x = np.array(x)
    y = np.array(y)

    list_of_tuples = list(zip(x, y))
    
    df = pd.DataFrame(list_of_tuples, 
                  columns = [x_arg_name, y_arg_name])
    
    df = df[df[y_arg_name].notna()]
    df = df[df[y_arg_name] >= 0.]
    return df[x_arg_name], df[y_arg_name]

dat_file = '/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/automation_binning_after_pf/test-scripts/xg-20210916_6956-20210916_6957-lyso9-199p6mm_unity_new_CCstar.dat' #sys.argv[1]

x_arg_name = 'd'
y_arg_name = 'CC*'


d_CCstar, CCstar = get_xy(dat_file, x_arg_name, y_arg_name)

CCstar *= 100

'''
CC2, d2 = y[0], x[0]
CC1, d1 = 0., 0.


resolution = -100


i = 0
while y[i]>=0.5 and i < len(x):
    CC1, d1 = CC2, d2
    i+=1
    CC2, d2 = y[i], x[i]
    if y[i] == 0.5:
        resolution = x[i]
        break
    

k = round((CC2-CC1)/(d2-d1),3)
b = round((CC1*d2-CC2*d1)/(d2-d1),3)    

resolution = round((0.5 -b) / k ,3)
print(resolution)

print(CC1, d1, CC2, d2)
print(k, b)
'''

rsplit_dat_file = '/gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/automation_binning_after_pf/test-scripts/xg-20210916_6956-20210916_6957-lyso9-199p6mm_unity_new_Rsplit.dat'
x_arg_name = 'd'
y_arg_name2 = 'Rsplit/%'

d_Rsplit, Rsplit = get_xy(rsplit_dat_file, x_arg_name, y_arg_name2)

i = 0

CC2, d2 = CCstar[0], d_CCstar[0]
CC1, d1 = 0., 0.

Rsplit2 = Rsplit[0]
Rsplit1 = 0.

while Rsplit[i]<=CCstar[i] and i < len(d_CCstar):
    CC1, d1, Rsplit1 = CC2, d2, Rsplit2
    i+=1
    CC2, d2, Rsplit2 = CCstar[i], d_CCstar[i], Rsplit[i]
    if Rsplit[i]==CCstar[i]:
        resolution = d_CCstar[i]
        break
        
print(CC1, d1, CC2, d2)
print(Rsplit1, d1, Rsplit2, d2)

k1 = round((CC2-CC1)/(d2-d1),3)
b1 = round((CC1*d2-CC2*d1)/(d2-d1),3)     

k2 = round((Rsplit2-Rsplit1)/(d2-d1),3)
b2 = round((Rsplit1*d2-Rsplit2*d1)/(d2-d1),3)

resolution = round(0.95*(b2-b1)/(k1-k2),3) 

print(resolution)