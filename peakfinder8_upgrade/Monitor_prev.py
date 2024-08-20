import os
import pyinotify
import sys
import h5py as h5
import numpy as np


import time

def calling_peakfinder8(file):
    dir_name = os.path.dirname(file) 
    job_file = os.path.join(dir_name, file.split('.')[0] + '.sh')
    with open(job_file, 'w+') as fh:
        fh.writelines("#!/bin/sh\n")
        fh.writelines("#SBATCH --job=%s.sh\n" % file.split('.')[0])
        fh.writelines("#SBATCH --partition=upex\n")
        fh.writelines("#SBATCH --time=12:00:00\n")
        fh.writelines("#SBATCH --nodes=1\n")
        fh.writelines("#SBATCH --mem=500000\n")
        fh.writelines("module load anaconda3/5.2\n")
        command = 'python3 /gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/peakfinder8_upgrade/pf8_coordinates_generating.py {}'.format(file)
        fh.writelines(command)
    os.system("sbatch %s" % job_file)


def Monitor(path):
    class PClose(pyinotify.ProcessEvent):
        def process_IN_CLOSE(self, event):
            f = event.name and os.path.join(event.path, event.name) or event.path
            '''
            here it is necessary to call pf8
            '''
            print(f)
            if 'data' in os.path.basename(f) and '.h5' in os.path.basename(f):
                calling_peakfinder8(f)
            
    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm, PClose())
    wm.add_watch(path, pyinotify.IN_CLOSE_WRITE)
    try:
        while 1:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()
    except KeyboardInterrupt:
        notifier.stop()
        return

if __name__ == '__main__':
    path = sys.argv[1]
    Monitor(path)