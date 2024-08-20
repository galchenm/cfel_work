import os
import sys
import re
from collections import defaultdict
import numpy as np


def prepare_blocks(blocks):
    d = defaultdict(dict)
    file = open(blocks, 'r')
    for line in file:
        
        if len(line)>0 and ':' in line:
            key,sample=line.strip().split(':')
            d[key]['sample'] = sample
            
            blocks = re.findall(r"[\w]+[_\d]*", key) #re.findall(r"\d+[_\d]*", key)
            delimeter = re.findall(r"[-,]", key)
            if ',' in delimeter or len(blocks) == 1:
                d[key]['blocks'] = blocks
            else: #delimeter is '-'
                if len(blocks) > 2:
                    print("WARNING: separate this line {} accroding to the rule of block file.\n".format(key))
                else:
                    f,l = blocks
                    
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
                        elif len(str(int(f)))== len(str(int(l))) and len(f) == len(l):
                            d[key]['blocks'] = [str(i) for i in np.arange(int(f), int(l) + 1)]
                        else:
                            pref = os.path.commonprefix([f,l])
                            if len(pref)>0:
                                ff = f.replace(pref,'')
                                ll = l.replace(pref,'')
                                d[key]['blocks'] = [pref+str(i) for i in np.arange(int(ff), int(ll) + 1)]
                            else:
                                d[key]['blocks'] = [str(i) for i in np.arange(int(f), int(l) + 1)]
    
    return d

def creating_lists(name_of_blocks):
    global blocks_dict
    global path_from
    global path_to
    global pattern
    global file_extension

    blocks = blocks_dict[name_of_blocks]['blocks']
    sample = blocks_dict[name_of_blocks]['sample']

    filenameLST = os.path.join(path_to,f'{name_of_blocks}-{sample}.lst')

    with open(filenameLST,'w+') as files_lst:
        for block in blocks:
            dir_from = os.path.join(path_from, block)
            if os.path.exists(dir_from):
                data_files = os.listdir(dir_from)
                files_of_interest = [os.path.join(dir_from, filename) for filename in data_files if (file_extension in filename and pattern in filename)]
                if len(files_of_interest) > 0:
                    for f in files_of_interest:
                        files_lst.write(f)
                        files_lst.write("\n")

if __name__ == "__main__":
    blocks = sys.argv[1]
    path_from = sys.argv[2]
    path_to = sys.argv[3]
    pattern = sys.argv[4]
    file_extension = sys.argv[5]

    blocks_dict = prepare_blocks(blocks)
    name_of_blocks = blocks_dict.keys()

    print(pattern)

    for name in name_of_blocks:
    	creating_lists(name)

    #with Pool(processes=10) as pool:
    #    pool.map(creating_lists, name_of_blocks)