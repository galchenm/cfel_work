#!/usr/bin/env python3
# coding: utf8

import os
import sys
import time
import numpy as np 
import subprocess

import sys
import re

os.nice(0)

def processing(all_paths, FILE_NAME1):
    #FILE_NAME1 = 'GXPARM.XDS'
    dic_old = {}
    delta_x = []
    delta_y = []
    data_array = []
    correct_paths = []
    center_x_wo_shift = []
    center_y_wo_shift = []

    for path in all_paths:
        if os.path.exists(os.path.join(path,FILE_NAME1)):
            correct_paths.append(path)
            with open(os.path.join(path,FILE_NAME1), 'rb') as fileflow1:
                
                line = fileflow1.readline()
                line = fileflow1.readline()
                line = fileflow1.readline()
                k_vect = line.split()
                lambd = float(k_vect[0])
                kx,ky,kz = [float(i)*lambd for i in k_vect[1:]]
                
                line = fileflow1.readline()
                line = fileflow1.readline()
                line = fileflow1.readline()
                line = fileflow1.readline()
                line = fileflow1.readline()
                data_array = line.split()
                res_x = float(data_array[-2])
                res_y = float(data_array[-1])
                line = fileflow1.readline()
                data_array = line.split()
                X = float(data_array[0])
                Y = float(data_array[1])

                detector_distance = float(data_array[2])               
                dX = kx * abs(detector_distance) / res_x
                dY = ky * abs(detector_distance) / res_y

                delta_x.append(dX)
                delta_y.append(dY)

                dic_old[path] = [np.array([X+dX, Y+dY]),np.array([dX,dY,kz])]
                print(X+dX, Y+dY)
        else:
            print('In current path {} file with name {} does not exist'.format(path, FILE_NAME1))        
            
        print('''current path is {}'''.format(path))

    dx_median = round(np.median(np.array(delta_x)),4)
    dy_median = round(np.median(np.array(delta_y)),4)

    sigma_dx = round(np.std(np.array(delta_x)),6)
    sigma_dy = round(np.std(np.array(delta_y)), 6)

    center_x = round(np.median([dic_old[i][0][0] for i in dic_old]),4)
    center_y = round(np.median([dic_old[i][0][1] for i in dic_old]),4)

    sigma_x = round(np.std([dic_old[i][0][0] for i in dic_old]),6)
    sigma_y = round(np.std([dic_old[i][0][1] for i in dic_old]),6)

    #med_kx = round(np.median([dic_old[i][1][0] for i in dic_old]),6)
    #med_ky = round(np.median([dic_old[i][1][1] for i in dic_old]),6)
    #med_kz = round(np.median([dic_old[i][1][2] for i in dic_old]),6)

    #k_vect = np.array([med_kx, med_ky, med_kz])
    #sigma_k_vect = np.array([sigma_dx,sigma_dy,round(np.std(np.array(med_kz)),6)])

    print('Detector center is ({}, {}),'.format(center_x,center_y))
    print('Standart deviation for center is ({}, {})'.format(sigma_x, sigma_y))

    #return dic_old, center_x, center_y, sigma_x, sigma_y,k_vect, sigma_k_vect, dx_median, dy_median
    return 0

if __name__ == "__main__":
    print ('''Specify the folder from which to start searching for suitable files (enter the appropriate number): \n 1: Current directory \n2: Folder name in the current directory \n3: Full path''')
    variant = int(sys.argv[1])

    if variant == 1:
        main_path = os.getcwd()
        #res = float(sys.argv[2])
    elif variant == 2:
        main_path = os.getcwd()
        str_dir = sys.argv[2]
        main_path = main_path + r'/' + str_dir
        #res = float(sys.argv[3])
    elif variant == 3:
        main_path = str(sys.argv[2])
        #res = float(sys.argv[3])
    else: 
        exit()

    print('''Main path = {}'''.format(main_path))


    # !!!!Specify the full name of the correct file of interest to us!!!!
    FILE_NAME1 = 'GXPARM.XDS'

    # Initialize an empty list, where later we add all the paths to our files
    all_paths = []

    for path, dirs, all_files in os.walk(main_path):
        for file in all_files:
            if file == FILE_NAME1:
                all_paths.append(path)

    for path in all_paths:
        if os.access(path, os.R_OK) == 'false':
            exit()

    print(all_paths)
    processing(all_paths, FILE_NAME1)

    print('FINISH')