import os
import pyinotify
import sys
import h5py as h5
import numpy as np
import glob

import time

def calling_peakfinder8(file):
    global output_dir
    #dir_name = '/asap3/petra3/gpfs/p11/2022/data/11013278/scratch_cc/galchenm/test_chip_pf8' 
    job_file = os.path.join(output_dir, os.path.basename(file).split('.')[0] + '.sh')
    print('process ', os.path.basename(file), '\n')
    with open(job_file, 'w+') as fh:
        fh.writelines("#!/bin/sh\n")
        fh.writelines("#SBATCH --job=%s.sh\n" % file.split('.')[0])
        fh.writelines("#SBATCH --partition=upex\n")
        fh.writelines("#SBATCH --time=12:00:00\n")
        fh.writelines("#SBATCH --nodes=1\n")
        fh.writelines("#SBATCH --mem=500000\n")
        fh.writelines("module load anaconda3/5.2\n")
        command = 'python3 /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/peakfinder8_upgrade/pf8_coordinates_generating.py {} {}'.format(file, output_dir)
        fh.writelines(command)
    #time.sleep(2.5)
    os.system("sbatch %s" % job_file)


def Monitor_pyinotify_v1(path):
    '''
    https://github.com/seb-m/pyinotify/wiki/Tutorial
    
    https://github.com/seb-m/pyinotify/wiki
    '''
    wm = pyinotify.WatchManager()  # Watch Manager
    mask = pyinotify.IN_CLOSE_WRITE| pyinotify.IN_CREATE  # watched events

    class EventHandler(pyinotify.ProcessEvent):
        def process(self, event):
            print("Creating:", event.pathname)

        #def process_IN_DELETE(self, event):
        #    print "Removing:", event.pathname


    notifier = pyinotify.ThreadedNotifier(wm, EventHandler())
    notifier.start()

    wdd = wm.add_watch(path, mask, rec=True)
    wm.rm_watch(wdd.values())

    notifier.stop()

def Monitor_pyinotify_old(path):
    class PClose(pyinotify.ProcessEvent):
        def process_IN_CLOSE(self, event):
            f = event.name and os.path.join(event.path, event.name) or event.path
            '''
            here it is necessary to call pf8
            '''
            print(f)
            if 'data' in os.path.basename(f) and '.h5' in os.path.basename(f):
                calling_peakfinder8(f)
        def process_IN_CREATE(self, event):
            pass
    print('call monitor')        
    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm, PClose())
    wm.add_watch(path, pyinotify.IN_CLOSE_WRITE | pyinotify.IN_CREATE)
    try:
        while 1:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()
    except KeyboardInterrupt:
        notifier.stop()
        return

def Monitor(path):
    
    list_of_files = glob.glob(f'{path}/*h5')
    processed = []
    after = len(list_of_files)
    while(after == 0):
        list_of_files =  glob.glob(f'{path}/*h5')
        after = len(list_of_files)
        
    #while(1):
    for file in list_of_files:
        if file not in processed and 'data' in os.path.basename(file):
            processed.append(file)
            #print(file)
            calling_peakfinder8(file)
    time.sleep(1)
    list_of_files = glob.glob(f'{path}/*h5')

    
if __name__ == '__main__':
    path = sys.argv[1]
    output_dir = sys.argv[2]
    while 1:
        #print(1)
        if os.path.exists(path):
            print('appeared')
            
            break
    Monitor(path)
