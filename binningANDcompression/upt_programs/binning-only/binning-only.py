import numpy
import os
import sys
import h5py as h5

'''
def detector_data(event: Dict[str, Any]) -> numpy.ndarray:
    """
    Retrieves one frame of Jungfrau detector data from files.
    Arguments:
        event (Dict[str, Any]): a dictionary storing the event data.
    Returns:
        numpy.ndarray: one frame of detector data.
    """
    # Returns the data from the Eiger HDF5 files
    data: numpy.ndarray = event["additional_info"]["h5file"]["entry/data/data"][event["additional_info"]["index"]]
    if event["additional_info"]["binning"] is True:
        mask: numpy.ndarray = event["additional_info"]["binning_bad_pixel_map"]
        min_pix_count: int = event["additional_info"]["binning_min_good_pixel_count"]
        if mask is None or mask.shape != data.shape:
            mask = numpy.ones(data.shape, dtype=numpy.int)        
        nx: int
        ny: int
        nx, ny = data.shape
        data_type: numpy.dtype = data.dtype

        #set bad pixels to zero:
        data = data * mask
        #binned data:
        data = data.reshape(nx // 2, 2, ny // 2, 2).sum(3).sum(1)
        
        #binned mask = num good pixels per bin
        mask_binned = mask.reshape(nx // 2, 2, ny // 2, 2).sum(3).sum(1)
        data = data / mask_binned * 4
        
        if numpy.issubdtype(data_type, numpy.integer):
            bad_pix_value: int = numpy.iinfo(data_type).max
            data[numpy.where(data > bad_pix_value)] = bad_pix_value
        else:
            bad_pix_value = numpy.nan
        data[numpy.where(mask_binned < min_pix_count)] = bad_pix_value
    
    return data
'''

def processing(data, mask, nx, ny, data_type, min_pix_count):
    #set bad pixels to zero:
    data = data * mask
    #binned data:
    data = data.reshape(nx // 2, 2, ny // 2, 2).sum(3).sum(1)

    #binned mask = num good pixels per bin
    mask_binned = mask.reshape(nx // 2, 2, ny // 2, 2).sum(3).sum(1)
    
    data = numpy.divide(data, mask_binned, out=numpy.zeros_like(data), where=mask_binned!=0) * 4 #data = data / mask_binned * 4
    
    if numpy.issubdtype(data_type, numpy.integer):
        bad_pix_value: int = numpy.iinfo(data_type).max
        data[numpy.where(data > bad_pix_value)] = bad_pix_value
    else:
        bad_pix_value = numpy.nan
    data[numpy.where(mask_binned < min_pix_count)] = bad_pix_value
    
    return data
 
filename = sys.argv[1]
path_to_data = sys.argv[2]
maskfilename = sys.argv[3]
h5maskpath = sys.argv[4]
min_pix_count = int(sys.argv[5])
output_path = sys.argv[6]

file = h5.File(filename, 'r')
data = file[path_to_data]

maskf = h5.File(maskfilename, 'r')
mask = maskf[h5maskpath][:,]

num, nx, ny = data.shape
shape_data = (nx // 2, ny // 2)
data_type = data.dtype

initShape = (1,) + shape_data
maxShape = (num,) + shape_data


new_filename = os.path.join(output_path, 'binned-' + os.path.basename(filename))
with h5.File(new_filename, 'w') as out:
    
    d = out.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=data_type, chunks=initShape, compression="gzip", compression_opts=6)
    d[0,] = processing(data[0,], mask, nx, ny, data_type, min_pix_count)
    
    for i in range(num):
        d.resize((i+1,) + shape_data)
        d[i,] = processing(data[i,], mask, nx, ny, data_type, min_pix_count)

file.close()
maskf.close()