import numpy as np
import matplotlib.pyplot as plt
import os
import re
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

d = defaultdict(list)

#streams = ['/asap3/petra3/gpfs/p11/2020/data/11010575/scratch_cc/galchenm/2711_62-63-lyso-upt/j_stream/2711_62-63-lyso.stream','/asap3/petra3/gpfs/p11/2020/data/11010575/scratch_cc/galchenm/2711_64-65-lyso-upt/j_stream/2711_64-65-lyso.stream','/asap3/petra3/gpfs/p11/2020/data/11010575/scratch_cc/galchenm/2711_66-67-lyso-upt/j_stream/2711_66-67-lyso.stream', '/asap3/petra3/gpfs/p11/2020/data/11010575/scratch_cc/galchenm/2711_68-69-lyso-upt/j_stream/2711_68-69-lyso.stream']

#streams = ['/asap3/petra3/gpfs/p11/2020/data/11010575/scratch_cc/galchenm/2711_68-69-lyso-upt/j_stream/2711_68-69-lyso.stream']

streams = ['/asap3/petra3/gpfs/p11/2021/data/11010507/scratch_cc/galchenm/raw-processed/20210916_6944-20210916_6946-lys-ont-tape-2s/j_stream/20210916_6944-20210916_6946-lys-ont-tape-2s.stream', '/asap3/petra3/gpfs/p11/2021/data/11010507/scratch_cc/galchenm/raw-processed/20210916_6940-20210916_6941-lys-ont-tape-4s/j_stream/20210916_6940-20210916_6941-lys-ont-tape-4s.stream', '/asap3/petra3/gpfs/p11/2021/data/11010507/scratch_cc/galchenm/raw-processed/20210916_6947-20210916_6948-lys-ont-tape-6s/j_stream/20210916_6947-20210916_6948-lys-ont-tape-6s.stream', '/asap3/petra3/gpfs/p11/2021/data/11010507/scratch_cc/galchenm/raw-processed/20210916_6949-20210916_6950-lys-ont-tape-8s/j_stream/20210916_6949-20210916_6950-lys-ont-tape-8s.stream']

for stream in streams:
    with open(stream, 'r') as file:
        found_file = False
        
        for line in file:
            if line.startswith('Image filename:'):
                name = os.path.basename(line.split()[-1])
                pattern = re.search(r'\d+[_]*\d+',name).group()
                
                #pattern = re.search(r'[\d]s',name).group()
                found_file = True
            elif line.startswith('diffraction_resolution_limit = '): # profile_radius
                #radius = float(re.search(r'\d+.\d+',line.strip()).group())
                diffraction_resolution_limit = float(re.search(r'\d+.\d+ A',line.strip()).group().split(' ')[0])
                if found_file:
                    #d[pattern].append(radius)
                    d[pattern].append(diffraction_resolution_limit)
                    found_file = False

print(d)

for run in d:
    #plt.figure()
    #plt.hist(d[run], bins=800, range=(0, 0.025), alpha = 0.5, label = run)
    data = np.array(d[run])
    #data=data[data]
    #sns.distplot(data[data<0.025],bins=100,hist=False, kde=True, label="{}, mean = {}, sigma = {}".format(run, round(np.mean(np.array(d[run])),3), round(np.std(np.array(d[run])),3)))
    #plt.savefig('{}, mean ={}, sigma = {}.png'.format(run, round(np.mean(np.array(d[run])),6), round(np.std(np.array(d[run])),6)))
    #plt.close()
    
    n,x,_ = plt.hist(data, bins=100, histtype=u'step', label="{},".format(run))
    #bin_centers = 0.5*(x[1:]+x[:-1])
    #plt.plot(bin_centers, n) ## using bin_centers rather than edges


plt.legend(prop ={'size': 10}) 
#plt.savefig('lyso-on-the-fly-update-11010507.png')
plt.show()
#plt.close()

