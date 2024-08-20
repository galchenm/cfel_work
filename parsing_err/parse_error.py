#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
import re

"""
python3 parse_error.py /gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/data_processing/cheetah_r0096/1192_xgandalf_test/error
"""

os.nice(0)

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass


def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('path_to_err', type=str, help="The path to error file")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_cmdline_args()
    error_path = args.path_to_err
    
    files_set = subprocess.check_output(['ls', error_path]).decode('utf-8').strip().split('\n')
    error_files = [i for i in files_set if 'err' in i]
    flag = False

    for err in error_files:
        try:
            n = int(subprocess.check_output(['grep','-c','not found', os.path.join(error_path, err)]).decode('utf-8').strip())
            if n != 0:
                machine_name = re.findall(r'[a-z]{4}[0-9]{3}',err.split('.err')[0])[0]
                print(err, machine_name)
                flag = True

        except subprocess.CalledProcessError as e:
            pass

    if not(flag):
        print("No error message")