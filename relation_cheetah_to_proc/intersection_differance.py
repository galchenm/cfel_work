#!/usr/bin/env python3

"""
python3 intersection_differance.py proc_r0095.csv cheetah_r0095.csv
Input: 2 csv files
Output: parsing each streams, their intersection and difference 
"""


import os
import sys
import h5py as h5
import subprocess
import re
import argparse
import pandas as pd


class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('first_csv', type=str, help="First input csv file")
    parser.add_argument('second_csv', type=str, help="Second input csv file")
    return parser.parse_args()



if __name__ == "__main__":
    args = parse_cmdline_args()
    df1 = args.first_csv
    df2 = args.second_csv


    print('Find intersection and differance between indexed patterns\n')
    mergedStuff = pd.merge(df1, df2, on=['train_ID', 'pulse_ID'], how='inner', suffixes=('_proc', '_cheetah')) #intersection
    diffferentStuff =  pd.concat([df1,df2]).drop_duplicates(subset=['train_ID', 'pulse_ID'], keep=False) #differance

    print('Saving results into csv\n')
    mergedStuff.to_csv(os.path.join(os.getcwd(), 'result_intersection.csv'), index = False, header=True, sep='\t')
    diffferentStuff.to_csv(os.path.join(os.getcwd(), 'result_diff.csv'), index = False, header=True, sep='\t')

    