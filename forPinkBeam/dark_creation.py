import os
import sys
import glob
import re
from collections import defaultdict

path_subpanels_darks = sys.argv[1]
output = sys.argv[2]

os.chdir(path_subpanels_darks)


list_of_files_d = glob.glob(os.path.join(path_subpanels_darks, '*d0_*.h5')) + glob.glob(os.path.join(path_subpanels_darks, '*d1_*.h5'))


d_dict = defaultdict(list) 

for file in list_of_files_d:
    name = os.path.basename(file)
    name = name.split('_f')[0]
    d_dict[name].append(file)
    


#os.system(command_line)

for key in d_dict:
    f = open(os.path.join(output,f'{key}.lst'),'w')
    files = "\n".join(d_dict[key])
    f.write(files)
    f.close()
    if not(os.path.exists(os.path.join(output, f'{key}.h5'))):
        command_line = "source /home/atolstik/miniforge3/envs/om//bin/activate \n"
        command_line += "om_jungfrau_dark.py " + os.path.join(output,f'{key}.lst') +" "+ os.path.join(output, f'{key}.h5')
        #command_line += "om_jungfrau_dark.py " + os.path.join(output,f'{key}.lst') +" "+ os.path.join(path_subpanels_darks, f'{key}.h5')
        os.system(command_line)
    else:
        print(f'{os.path.join(output, key+".h5")} is already created')
    
    




