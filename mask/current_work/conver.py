
#!/usr/bin/env python3

"""
WRITE MESSAGE HERE

python3 join_converter.py r0014_detectors_virt.cxi /entry_1/instrument_1/detector_1/data /entry_1/instrument_1/detector_1/mask

"""


import os
import sys
import h5py as h5
import numpy as np
import subprocess
import re
import argparse



os.nice(0)
'''
class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('file_cxi', type=str, help="Output file of cxi format")
    parser.add_argument('maskH5', type=str, help="hdf5 path for the cxi file mask")
    parser.add_argument('slab',type=str, help="2D mask file")
    parser.add_argument('-m', '--mask_h5path', type=str, help="hdf5 path to slab mask data")

    return parser.parse_args()
'''

def converting_slab_to_3D(mask_file, path_to_mask):

    print('Starting reshaping mask from 2D to 3D\n')

    f = h5.File(mask_file, 'r')
    slab_mask = np.array(f[path_to_mask])
    dim = slab_mask.shape
    f.close()
    mask_3D = np.array(np.reshape(slab_mask.ravel(),(dim[0]//512, 512, dim[1])))
    print('Finish reshaping\n')

    return mask_3D

def inversion_mask(mask_data):
    print('Inversion of static mask\n')
    inv_mask_data = np.ones_like(mask_data) - mask_data
    return inv_mask_data



if __name__ == "__main__":
    '''
    args = parse_cmdline_args()

    file_cxi = args.file_cxi
    mask_cxi = args.maskH5
    slab = args.slab
    mask_slab = "/data/data"

    if args.mask_h5path is not None:
        mask_slab = args.mask_h5path


    '''

    file_cxi = "r0014_detectors_virt.cxi"
    mask_cxi = "/entry_1/instrument_1/detector_1/mask"
    slab = "mask_lyso.h5"
    #slab = "slab_mask.h5"
    mask_slab = "/data/data"

    #Converting slab mask into 3D
    mask_3D = converting_slab_to_3D(slab, mask_slab)
    
    #Inversion of mask
    mask_3D_inv = inversion_mask(mask_3D) # 1 - bad, 0 - good
    num_events = subprocess.check_output(['/opt/hdf5/hdf5-1.10.5/bin/h5ls', str(os.path.join(os.getcwd(),file_cxi))+str(mask_cxi)])
    num_events = num_events.strip().decode('utf-8').split('Dataset ')[1]
    num = int(re.sub(r'({|})', '', num_events).split(',')[0]) # Number of events
    print('NUM = {}'.format(num))

    #Make o copy of initial cxi file

    h5r = h5.File(file_cxi, 'r')
    copy_cxi = file_cxi.split('.')[0] + '_copy_lyso.cxi'
    
    members = []
    h5r.visit(members.append)

    with h5.File(copy_cxi, 'w') as h5w:
        for obj in members:
            if obj != mask_cxi[1:] and not isinstance(h5r[obj], h5.Group):        
                group_path = h5r[obj].parent.name
                
                # Check that this group exists in the destination file; if it doesn't, create it
                # This will create the parents too, if they don't exist
                group_id = h5w.require_group(group_path)
                h5r.copy(obj, group_id, expand_external=True, expand_refs=True, without_attrs=True)
            elif obj == mask_cxi[1:]:
                print('Union event mask with static mask\n')
                d = h5w.create_dataset(obj, (1,16,512,128), maxshape=(num,16,512,128), dtype=np.float32,chunks=(1,16,512,128), compression="gzip", compression_opts=4)
                mask = h5r[mask_cxi]
                for i in range(num):
                    d.resize((i+1,16,512,128))
                    slice_arr = mask[i,:,:,:]
                    slice_arr = np.array(slice_arr)
                    index_bad = np.where(slice_arr > 0)
                    
                    slice_arr_upt = np.zeros_like(slice_arr)
                    slice_arr_upt[index_bad] = 1

                    C = np.bitwise_or(slice_arr_upt, mask_3D_inv)
                    C[index_bad] = slice_arr[index_bad]
                    d[i, :, :,:] = C
                     
            else:
                pass   

    h5r.close()





