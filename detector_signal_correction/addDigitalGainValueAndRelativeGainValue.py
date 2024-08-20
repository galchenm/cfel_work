import h5py as h5
import matplotlib.pyplot as plt

#fig, axs = plt.subplots(1, 2)
'''
file1 = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/res/Cheetah-calib-AGIPD01.h5'
dark_signal = "/AnalogOffset"
badpixel='/Badpixel'
bbad = '/BadPixel'
f1 = h5.File(file1, 'r')
#data = f1[bbad][0,0,]
data = f1[dark_signal][0,0,]
print(data.shape)
axs[0].imshow(data, cmap='viridis')
axs[0].set_title('My 14 panel 0 cellID')
#plt.show()


file2 = '/gpfs/exfel/u/scratch/SPB/202002/p002442/cheetah/calib/agipd/r0138-r0141-r0140/Cheetah-AGIPD01-calib.h5'

path = '/AnalogOffset'

f2 = h5.File(file2, 'r')
#data2 = f2[badpixel][0,0,]
data2 = f2[path][0,0,]
print(data2.shape)
axs[1].imshow(data2, cmap='viridis')
axs[1].set_title("Oleksandra's 14 panel 0 cellID")
plt.show()
'''

import glob
import os

path_from = '/gpfs/exfel/u/scratch/SPB/202002/p002442/cheetah/calib/agipd/r0138-r0141-r0140'
path_to = '/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/darks/darks141_all'
files_from = glob.glob(os.path.join(path_from,"*.h5"))
files_to = glob.glob(os.path.join(path_to,"*.h5"))

print(files_from)
DigitalGainLevel = '/DigitalGainLevel'
RelativeGain ='/RelativeGain'

for file in files_from:
    filename = os.path.basename(file)
    file_read = h5.File(file, 'r')
    file_write = h5.File(os.path.join(path_to, filename), 'a')
    dataDigitalGainLevel = file_read[DigitalGainLevel]
    dataRelativeGain = file_read[RelativeGain]
    print(dataDigitalGainLevel.shape, dataRelativeGain.shape)
    file_write.create_dataset(DigitalGainLevel, data=dataDigitalGainLevel)
    file_write.create_dataset(RelativeGain, data=dataRelativeGain)
    file_write.close()
    file_read.close()
