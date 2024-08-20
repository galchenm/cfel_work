
import os
import time

from collections import defaultdict

import re
#import argparse

from subprocess import call
import shlex

import pandas as pd
import glob

time_delay= None
path_from = "/asap3/petra3/gpfs/p11/2020/data/11009046/raw"
path_to ="/asap3/petra3/gpfs/p11/2020/data/11009046/scratch_cc/galchenm/processed/tmp"


'''
dic_in_path_from = defaultdict(list)

for path, dirs, all_files in os.walk(path_from):
    for di in dirs:
        if re.search(r"[run]*[\d]+", di) and (time.time() - os.stat(os.path.join(path, di)).st_mtime > time_delay):
            d_name = re.sub(r"[run]", '', di)
            dic_in_path_from[d_name]=di

folders_in_path_from = dic_in_path_from.keys()



for path, dirs, all_files in os.walk(path_to):
    for file in all_files:
        if re.search(r"lst$", file):
            filename = re.search(r"[run]*[\d]+[_\d]*", file).group()
            if re.search(r"[run]*[\d]+", filename):
                filename = re.sub(r"[run]", '', filename)
                folders_in_path_to.append(filename)

folders_need_to_add = list(set(folders_in_path_from) - set(folders_in_path_to))


dic_runs_all = defaultdict(list)

for current_run in folders_need_to_add:
    
    dir_from = os.path.join(path_from, dic_in_path_from[current_run])
    
    if os.path.exists(dir_from):
        
        data_files = os.listdir(dir_from)
        files_of_interest = [os.path.join(dir_from, filename) for filename in data_files if (".h5" in filename or ".cxi" in filename) and "data" in filename]
        
        if len(files_of_interest) > 0:

            new_dir = os.path.join(path_to, current_run)
            if not(os.path.exists(new_dir)):
                
                os.mkdir(new_dir)

            file_lst_name = os.path.join(new_dir, current_run +".lst")

            dic_runs_all[current_run] = os.path.abspath(file_lst_name)

            files_lst = open(file_lst_name, 'w+')
            for f in files_of_interest:
                files_lst.write(f)
                files_lst.write("\n")
            files_lst.close()

os.chdir(path_to)

if len(dic_runs_all.keys()) == 0:
    runs_from = folders_in_path_to
else:
    runs_from = dic_runs_all.keys()
'''

file_df = "/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/auto_running_turbo_index/test.xls"
df_geom = pd.read_excel(file_df, header=0, sheet_name="geom")

folders_in_path_to = []

for path, dirs, all_files in os.walk(path_to):
    for file in all_files:
        if re.search(r"lst$", file) and re.search(r"[run]*[\d]+[_\d]*", file):
            filename = re.search(r"[run]*[\d]+[_\d]*", file).group()
            if re.search(r"[run]*[\d]+", filename):
                filename = re.sub(r"[run]", '', filename)
                folders_in_path_to.append(filename)

runs_from = folders_in_path_to

df_data = pd.read_excel(file_df, header=0, sheet_name="data")
df_data = df_data.drop_duplicates()  # delete duplicate rows
runs = df_data['run']

df_pdb = pd.read_excel(file_df, header=0, sheet_name="pdb")

for run in runs:
    current_run = str(run)
    current_dir = os.path.join(path_to, current_run)

    if os.path.exists(current_dir):
        if not(os.path.exists(os.path.join(current_dir, "error"))):
            os.mkdir(os.path.join(current_dir, "error"))
        if not(os.path.exists(os.path.join(current_dir, "streams"))):
            os.mkdir(os.path.join(current_dir, "streams"))
        error_dir = os.path.join(current_dir, "error")
        streams_dir = os.path.join(current_dir, "streams")

        os.chdir(current_dir)
        files = glob.glob("*.lst")
        filename_lst = current_run + ".lst"

        if filename_lst in files:
            if current_run in runs_from:
                info = df_data[df_data['run'] == run]
                mode = info['mode'].item()

                substrate = info['type'].item()
                detector_distance = info['distance'].item()
                processed = info['processed'].item()

                if pd.isnull(mode) or pd.isnull(detector_distance) or pd.isnull(substrate):
                    print(
                        "WARNING: Run {} doesn't have one of these fields: mode, distance, type. Check it.".format(run))
                else:
                    geom = df_geom[(df_geom['mode'] == mode) & (df_geom['distance'] == detector_distance)][
                        'geom'].item()
                    pdb = df_pdb[df_pdb['type'] == substrate]['pdb'].item()

                if pd.isnull(processed):
                    print("Run {} is not processed".format(run))
                    command_line = "bash /gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/auto_running_turbo_index/turbo-index-uni {} {} {} {} {}".format(
                        os.path.abspath(filename_lst), geom, streams_dir, error_dir, pdb)

                    status_file = open(os.path.join(current_dir, "status.txt"), "w+")
                    status_file.write("FINISHED")
                    status_file.close()
                    #call(shlex.split(command_line))

                    df_data.loc[df_data['run'] == run, 'processed'] = "done"
                else:
                    print("Run {} has been already processed".format(run))

            else:
                print("WARNING: The run {} exists in CSV, but is not found between folders".format(current_run))
        else:
            print("WARNING: There is no list of HDF5 files in {}".format(current_dir))
    else:
        print("WARNING: This run {} doesn't exist in {}".format(current_run, path_from))




