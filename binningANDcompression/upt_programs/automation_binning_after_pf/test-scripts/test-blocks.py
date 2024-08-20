import os
import re
from collections import defaultdict
import numpy as np
import glob


def prepare_blocks(blocks):
    d = defaultdict(dict)
    file = open(blocks, 'r')
    for line in file:
        key,sample=line.strip().split(':') if len(line.strip().split(':')) > 1 else line.strip().split(':')[0], ''
        
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
                    else:
                        pref = os.path.commonprefix([f,l])
                        if len(pref)>0:
                            ff = f.replace(pref,'')
                            ll = l.replace(pref,'')
                            d[key]['blocks'] = [pref+str(i) for i in np.arange(int(ff), int(ll) + 1)]
                        else:
                            d[key]['blocks'] = [str(i) for i in np.arange(int(f), int(l) + 1)]
    
    return d


filename = '/asap3/petra3/gpfs/p11/2021/data/11010929/scratch_cc/galchenm/binning-test/process-binned/lacta.lst'
raw_data = '/asap3/petra3/gpfs/p11/2021/data/11010929/scratch_cc/galchenm/binning-test/process-binned'

d = prepare_blocks(filename)
print(d.keys())


print(os.listdir(raw_data))
folders = os.listdir(raw_data)
for key in d:
    folder = os.path.join(raw_data, list(filter(lambda element: key in element, folders))[0])
    print(folder)
    print(d[key]['blocks'])
    print(glob.glob(f'{folder}/**/*.stream', recursive=True)[0]) # stream file for parsing for template
    print(glob.glob(f'{folder}/**/*CCstar.dat', recursive=True)[0]) # stream file for parsing for template