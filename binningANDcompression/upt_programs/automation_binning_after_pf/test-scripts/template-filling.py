#!/usr/bin/env python3
# coding: utf8
# Written by Galchenkova M., 2021

import os
import sys
import subprocess
from string import Template
import shlex
import re

stream_filename = sys.argv[1]
bin_size = 2 #sys.argv[3]
min_good_pix_count = 3 #sys.argv[4]
max_res = 600 #sys.argv[5]

output = os.path.dirname(os.path.abspath(stream_filename))  #sys.argv[2]
print(output)
os.chdir(output)

try:
    command = f'grep -e indexamajig {stream_filename}'
    result = subprocess.check_output(shlex.split(command)).decode('utf-8').strip().split('\n')[0]
    geometry_file = '/'+re.findall(r"\b\S+\.geom", result)[0]

    min_num_peaks_for_hit = re.findall(r"\-\-min\-peaks=\d+", result)
    min_num_peaks_for_hit = int(min_num_peaks_for_hit[0].split('=')[-1]) if len(min_num_peaks_for_hit)>0 else 10

    max_num_peaks_for_hit = re.findall(r"\-\-max\-peaks=\d+", result)
    max_num_peaks_for_hit = int(max_num_peaks_for_hit[0].split('=')[-1]) if len(max_num_peaks_for_hit)>0 else 5000
    
    adc_threshold = re.findall(r"\-\-threshold=\d+", result)
    adc_threshold = int(adc_threshold[0].split('=')[-1]) if len(adc_threshold)>0 else 10
    
    minimum_snr = re.findall(r"\-\-min\-snr=\d+\.\d*", result)
    minimum_snr = float(minimum_snr[0].split('=')[-1]) if len(minimum_snr)>0 else 4.5
   
    min_pixel_count = re.findall(r"\-\-min\-pix\-count=\d+", result)
    min_pixel_count = int(min_pixel_count[0].split('=')[-1]) if len(min_pixel_count)>0 else 1

    max_pixel_count = re.findall(r"\-\-max\-pix\-count=\d+", result)
    max_pixel_count = int(max_pixel_count[0].split('=')[-1]) if len(max_pixel_count)>0 else 50
    
    min_res = re.findall(r"\-\-min\-res=\d+", result)
    min_res = int(min_res[0].split('=')[-1]) if len(min_res)>0 else 10

    local_bg_radius = re.findall(r"\-\-local\-bg\-radius=\d+", result)
    local_bg_radius = int(local_bg_radius[0].split('=')[-1]) if len(local_bg_radius)>0 else 4
 
    command = f'grep -e mask_file {stream_filename}'
    result = subprocess.check_output(shlex.split(command)).decode('utf-8').strip().split('\n')[0]
    bad_pixel_map_filename = '/'+re.findall(r"\b\S+\.h5", result)[0]

    command = f'grep -e "mask =" {stream_filename}'
    result = subprocess.check_output(shlex.split(command)).decode('utf-8').strip().split('\n')[0]
    bad_pixel_map_hdf5_path = result.replace(' ','').split('=')[-1]
   

except subprocess.CalledProcessError:
    pass

command = "cp /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/automation_binning_after_pf/templates/template-work.yaml ./template.yaml"
os.system(command)



template_data = {"GEOMETRY":geometry_file, "MINPEAKS":min_num_peaks_for_hit, "MAXPEAKS":max_num_peaks_for_hit, "BINSIZE":bin_size, "MASKFILE":bad_pixel_map_filename, "MASKPATH":bad_pixel_map_hdf5_path, "MINGOODPIXCOUNT":min_good_pix_count, "THRESHOLD":adc_threshold, "MINSNR":minimum_snr, "MINPIXCOUNT":min_pixel_count,"MAXPIXCOUNT":max_pixel_count, "LOCALBGRADIUS":local_bg_radius, "MINRES":min_res, "MAXRES":max_res}

monitor_file = open('monitor.yaml', 'w')
with open('template.yaml', 'r') as f:
    src = Template(f.read())
    result = src.substitute(template_data)
    monitor_file.write(result)
monitor_file.close()
os.remove('template.yaml')
