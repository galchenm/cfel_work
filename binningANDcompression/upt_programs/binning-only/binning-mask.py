import numpy
import os
import sys
import h5py as h5


#def processing(data, mask, nx, ny, data_type, min_pix_count):
def processing(data, nx, ny):
    data = data.reshape(nx // 2, 2, ny // 2, 2).sum(3).sum(1)
    data = data // 4
    return data
 
filename = sys.argv[1]
path_to_data = sys.argv[2]
output_path = sys.argv[3]

file = h5.File(filename, 'r')
data = file[path_to_data][()]

nx, ny = data.shape
shape_data = (nx // 2, ny // 2)
data_type = data.dtype


new_filename = os.path.join(output_path, 'binned-' + os.path.basename(filename))
with h5.File(new_filename, 'w') as out:
    
    d = out.create_dataset(path_to_data, data=processing(data, nx, ny), dtype=data_type, compression="gzip", compression_opts=6)

    


file.close()
