#!/usr/bin/env python3
# coding: utf8
# Written by Galchenkova M.

import os
import sys
import re
from collections import defaultdict
import numpy as np
from multiprocessing import Pool, TimeoutError
import click

def prepare_blocks(blocks):
    d = defaultdict(dict)
    file = open(blocks, 'r')
    for line in file:
        tmp = line.strip().split(':')
        print(tmp, len(tmp))
        key, sample = tmp if len(tmp) > 1 else [tmp[0], None] 
        print(key, sample)
        d[key]['sample'] = sample
        
        blocks = re.findall(r"[\w]+[_\d]*", key) #re.findall(r"\d+[_\d]*", key)
        print(blocks)
        delimeter = re.findall(r"[-,]", key)
        if ',' in delimeter or len(blocks) == 1:
            d[key]['blocks'] = blocks
        else: #delimeter is '-'
            if len(blocks) > 2:
                print("WARNING: separate this line {} accroding to the rule of block file.\n".format(key))
            else:
                f,l = blocks
                print(f)
                print(l)
                if re.search(r"_",f) and re.search(r"_", l):
                    f_suf = re.sub(r"_",'', re.findall(r"_\d+",f)[0])
                    f_pref = re.sub(r"_",'', re.findall(r"\w+_",f)[0])
                    l_suf = re.sub(r"_",'', re.findall(r"_\d+",l)[0])
                    l_pref = re.sub(r"_",'', re.findall(r"\w+_",l)[0])

                    if f_pref != l_pref:
                        print("WARNING: this line {} could not be processed, because they have various prefix. Split these blocks into blocks with the same prefix!\n".format(key))
                        d[key]['blocks'] = []
                    else:
                        r = np.arange(int(f_suf), int(l_suf) + 1)
                        rr = [f_pref+"_"+str(i) for i in r]
                        d[key]['blocks'] = rr
                elif re.search(r"_",f) and not re.search(r"_", l) or not re.search(r"_",f) and re.search(r"_", l):
                    print("WARNING: this line {} could not be processed because parts have different type of name! Split them.\n".format(key))
                else:
                    if len(str(int(f)))!= len(str(int(l))) and len(f) == len(l):
                        pref = os.path.commonprefix([f,l])
                        d[key]['blocks'] = [pref + str(i) if len(pref + str(i)) == len(f) else pref + pref[0 : len(f) - len(pref + str(i))] + str(i) for i in np.arange(int(f), int(l) + 1)]
                    else:
                        pref = os.path.commonprefix([f,l])
                        
                        if len(pref)>0:
                            ff = f.replace(pref,'',1)
                            ll = l.replace(pref,'',1)
                            d[key]['blocks'] = [pref+str(i) for i in np.arange(int(ff), int(ll) + 1)]
                        else:
                            d[key]['blocks'] = [str(i) for i in np.arange(int(f), int(l) + 1)]
    
    return d
    
def creating_files_for_exfel_beamtimes(parameters):
    name_of_blocks, path_to, path_from, file_extension = parameters
    if os.path.exists(f'{path_to}/{name_of_blocks}.lst'): #this is necessary to avoid to duplicate files
        os.remove(f'{path_to}/{name_of_blocks}.lst')
    command = f"find {os.path.join(path_from, name_of_blocks)} -maxdepth 1 -name '*{file_extension}' >> {path_to}/{name_of_blocks}.lst"
    os.system(command)

def creating_lists(parameters):
    global blocks_dict
    
    name_of_blocks, path_to, path_from, pattern, file_extension, excluded = parameters
    #print(name_of_blocks, path_to, path_from, pattern, file_extension, excluded)
    
    try:
        blocks = blocks_dict[name_of_blocks]['blocks']
        sample = blocks_dict[name_of_blocks]['sample']
        filenameLST = os.path.join(path_to,f'{name_of_blocks}-{sample}.lst') if len(sample)>0 else os.path.join(path_to,f'{name_of_blocks}.lst')

        with open(filenameLST,'w+') as files_lst:
            for block in blocks:
                dir_from = os.path.join(path_from, block)
                if os.path.exists(dir_from):
                    data_files = os.listdir(dir_from)
                    files_of_interest = [os.path.join(dir_from, filename) for filename in data_files if (file_extension in filename and pattern in filename and not(excluded in filename))]
                    #print(files_of_interest)
                    files_of_interest.sort()
                    if len(files_of_interest) > 0:
                        for f in files_of_interest:
                            files_lst.write(f)
                            files_lst.write("\n")
                else:
                    print(f'Check {dir_from}')        
    except KeyError:
        pass



@click.command(context_settings=dict(help_option_names=["-h", "--help"]))

@click.argument(
    "blocks",
    nargs=1,
    type=click.Path(exists=True),
)

@click.argument(
    "path_from",
    nargs=1,
    type=click.Path(exists=True),
)


@click.argument(
    "path_to",
    nargs=1,
    type=click.Path(exists=True),
)

@click.option(
    "--p",
    "-p",
    "pattern",
    nargs=1,
    type=str,
    default='run',
    required=False,
)

@click.option(
    "--fe",
    "-fe",
    "file_extension",
    nargs=1,
    type=str,
    default='h5',
    required=False,
)

@click.option(
    "--e",
    "-e",
    "excluded",
    nargs=1,
    type=str,
    default='sum',
    required=False,
)


def main(blocks, path_from, path_to, pattern, file_extension, excluded):
    if file_extension == 'cxi':
        name_of_blocks = []
        with open(blocks, 'r') as file:
            for line in file:
                name_of_blocks.append(line.strip())

        with Pool(processes=len(name_of_blocks)) as pool:
            pool.map(creating_files_for_exfel_beamtimes, zip(name_of_blocks, [path_to]*len(name_of_blocks), [path_from]*len(name_of_blocks), [file_extension]*len(name_of_blocks)))
        
    else:
        global blocks_dict
        
        blocks_dict = prepare_blocks(blocks)
        name_of_blocks = blocks_dict.keys()
        print(name_of_blocks)

        with Pool(processes=10) as pool:
            pool.map(creating_lists, zip(name_of_blocks, [path_to]*len(name_of_blocks), [path_from]*len(name_of_blocks), [pattern]*len(name_of_blocks), [file_extension]*len(name_of_blocks), [excluded]*len(name_of_blocks)))
    print('Finished')

if __name__ == "__main__":  
    main()