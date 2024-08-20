import numpy as np
import matplotlib.pyplot as plt
import os
import re
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np



data = defaultdict(dict)
d = defaultdict(list)


#streams = ['/asap3/petra3/gpfs/p11/2021/data/11010507/scratch_cc/galchenm/raw-processed/20210916_6944-20210916_6946-lys-ont-tape-2s/j_stream/xg-20210916_6944-20210916_6946-lys-ont-tape-2s-199p6mm.stream', '/asap3/petra3/gpfs/p11/2021/data/11010507/scratch_cc/galchenm/raw-processed/20210916_6940-20210916_6941-lys-ont-tape-4s/j_stream/xg-20210916_6940-20210916_6941-lys-ont-tape-4s-199p6mm.stream', '/asap3/petra3/gpfs/p11/2021/data/11010507/scratch_cc/galchenm/raw-processed/20210916_6947-20210916_6948-lys-ont-tape-6s/j_stream/xg-20210916_6947-20210916_6948-lys-ont-tape-6s-199p6mm.stream', '/asap3/petra3/gpfs/p11/2021/data/11010507/scratch_cc/galchenm/raw-processed/20210916_6949-20210916_6950-lys-ont-tape-8s/j_stream/xg-20210916_6949-20210916_6950-lys-ont-tape-8s-199p6mm.stream']
#streams = ['/asap3/petra3/gpfs/p11/2021/data/11010507/scratch_cc/galchenm/raw-processed/20210916_6944-20210916_6946-lys-ont-tape-2s/j_stream/xg-20210916_6944-20210916_6946-lys-ont-tape-2s-199p6mm.stream']

streams = ['/asap3/petra3/gpfs/p11/2021/data/11010507/scratch_cc/galchenm/raw-processed/20210916_6944-20210916_6946-lys-ont-tape-2s/j_stream/20210916_6944-20210916_6946-lys-ont-tape-2s.stream', '/asap3/petra3/gpfs/p11/2021/data/11010507/scratch_cc/galchenm/raw-processed/20210916_6940-20210916_6941-lys-ont-tape-4s/j_stream/20210916_6940-20210916_6941-lys-ont-tape-4s.stream', '/asap3/petra3/gpfs/p11/2021/data/11010507/scratch_cc/galchenm/raw-processed/20210916_6947-20210916_6948-lys-ont-tape-6s/j_stream/20210916_6947-20210916_6948-lys-ont-tape-6s.stream', '/asap3/petra3/gpfs/p11/2021/data/11010507/scratch_cc/galchenm/raw-processed/20210916_6949-20210916_6950-lys-ont-tape-8s/j_stream/20210916_6949-20210916_6950-lys-ont-tape-8s.stream']

for stream in streams:
    with open(stream, 'r') as file:
        
        in_list = 0
        for line in file:
            if line.startswith('Image filename:'):
                name_of_file = line.split()[-1]
                print(name_of_file)
                continue
            if line.startswith('Event:'):
                event = line.split('//')[-1]
                if "{} //{}".format(name_of_file, event) not in data:
                    data["{} //{}".format(name_of_file, event)] = {'Int':0, 'N':0}
                continue
            if line.find("Reflections measured after indexing") != -1:
                in_list = 1
                continue
            if line.find("End of reflections") != -1:
                in_list = 0
            if in_list == 1:
                in_list = 2
                continue
            elif in_list != 2:
                continue

            # From here, we are definitely handling a reflection line

            # Add reflection to list
            columns = line.split()
            
            try:
                data["{} //{}".format(name_of_file, event)]['Int'] += float(columns[3])
                data["{} //{}".format(name_of_file, event)]['N'] += 1
            except:
                print("Error with line: "+line.rstrip("\r\n"))

for key in data.keys():
    try:
        name = os.path.basename(key.split('//')[0].strip()) #жопа
        pattern = re.search(r'\d+[_]*\d+',name).group()
        AvrInt = np.round(data[key]['Int'] / data[key]['N'], 2)
        d[pattern].append(AvrInt)
    except:
        
        pass

print(d.keys())

for run in d:
    #plt.figure()
    #plt.hist(d[run], bins=800, range=(0, 0.025), alpha = 0.5, label = run)
    ddata = np.array(d[run])
    #ddata=data[ddata<0.025]
    
    #sns.distplot(data[data<0.025],bins=100,hist=False, kde=True, label="{}, mean = {}, sigma = {}".format(run, round(np.mean(np.array(d[run])),3), round(np.std(np.array(d[run])),3)))
    #plt.savefig('{}, mean ={}, sigma = {}.png'.format(run, round(np.mean(np.array(d[run])),6), round(np.std(np.array(d[run])),6)))
    #plt.close()
    
    #n,x,_ = plt.hist(data, bins=100, histtype=u'step', label="{}, mean = {}, sigma = {}".format(run, round(np.mean(np.array(d[run])),3), round(np.std(np.array(d[run])),3)))
    plt.hist(ddata, bins=100,histtype=u'step', label="{}".format(run))
    #bin_centers = 0.5*(x[1:]+x[:-1])
    #plt.plot(bin_centers, n) ## using bin_centers rather than edges


plt.legend(prop ={'size': 10}) 
plt.show()
#plt.savefig('all-upt5.png')
#plt.close()
