import os
import subprocess
import sys
import re
import numpy as np
stream = sys.argv[1]
treshold = int(sys.argv[2])
res = subprocess.check_output(['grep', '-r', 'num_peaks',stream]).decode('utf-8').strip().split('\n')
numbers = np.array([int(re.search(r'\d+',i).group()) for i in res])
hits = np.sum(np.where(numbers > treshold, 1, 0))
print('In ' + os.path.basename(stream) + ' hits = {}'.format(hits))