import os
import glob
import sys

path_from = sys.argv[1]
path_to = sys.argv[2]

files = glob.glob(os.path.join(path_from, '*.lst'))

for file in files:
    filename = os.path.basename(file)
    name = os.path.join(path_to, filename.split('.')[0])
    if not os.path.exists(name):
        os.mkdir(name)
        os.mkdir(os.path.join(name, 'streams'))
        os.mkdir(os.path.join(name, 'tmp'))
        #os.mkdir(os.path.join(name, 'j_stream'))
        #os.mkdir(os.path.join(name, 'j_stream/error'))

