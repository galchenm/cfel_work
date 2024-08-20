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


def get_initial_patterns_from_INP(all_paths):
    dic = {}
    dic_distance = {}
    FILE_NAME2 = 'XDS.INP'
    k_vect = []

    for path in all_paths:
        os.chdir(path)
        
        with open(os.path.join(path,FILE_NAME2),'r') as f1:
            lines = f1.readlines()
        for line in lines:
            if line.startswith('ORGX=') and not(line.startswith('!')): 
                x,y = [float(i.split('=')[1]) for i in line.split(' ')]
            elif line.startswith('INCIDENT_BEAM_DIRECTION') and not(line.startswith('!')):
                k_vect = [float(i) for i in (line.split('=')[1]).split(' ')]

            elif line.startswith('DETECTOR_DISTANCE') and not(line.startswith('!')):
                detector_distance = float(line.split('=')[1])
                dic[path] = [np.array([x,y]), np.array(k_vect), detector_distance]
                if detector_distance not in dic_distance:
                    dic_distance[detector_distance] = np.array([x,y])
                break
                
    median_x = round(np.median([dic[i][0][0] for i in dic]),4) 
    median_y = round(np.median([dic[i][0][1] for i in dic]),4) 
    median_k = [round(np.median([dic[i][1][0] for i in dic]),4), round(np.median([dic[i][1][1] for i in dic]),4), round(np.median([dic[i][1][2] for i in dic]),4)]
    deviation_x = round(np.std([dic[i][0][0] for i in dic]),6) 
    deviation_y = round(np.std([dic[i][0][1] for i in dic]),6) 
    deviation_k = [round(np.std([dic[i][1][0] for i in dic]),6), round(np.std([dic[i][1][1] for i in dic]),6), round(np.std([dic[i][1][2] for i in dic]),6)]
    
    for i in dic_distance:
        print('For detector distance = {} the center is ({}, {})'.format(i,dic_distance[i][0],dic_distance[i][1]))
    return dic 

def processing(all_paths, FILE_NAME1): # GXPARM or XPARM
    dic_old = {}
    delta_x = []
    delta_y = []
    data_array = []
    correct_paths = []

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

    #dx_median = round(np.median(np.array(delta_x)),4)
    #dy_median = round(np.median(np.array(delta_y)),4)

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

    return 0