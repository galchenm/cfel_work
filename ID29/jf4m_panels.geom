; 
; Optimized panel offsets can be found at the end of the file
photon_energy = 11500 ;11560 eV    ; dependent of the experiment, can be imported from a HDF5 file
photon_energy_bandwidth = 0.01
; adu_per_eV = 8.6505-05 ; dependent of the experiment (equal to 1 over photon energy in eV)
adu_per_photon = 1       ; use it instead of adu_per_eV
clen = 0.1766 ;0.1756 ;0.1771 ;0.1766 ;0.1767 ;0.1768 ;0.1766 ;0.177 ;0.17738 ;0.176446
coffset = -0.000118
res = 13333.3            ; 75 micron pixel size

flag_morethan = 21000000

dim0 = %
dim1 = ss
dim2 = fs
data = /entry_0000/instrument/SlsDetector/data


;mask_file = /gpfs/cfel/group/cxi/scratch/2021/ESRF-2022-Obertuer-Dec-ID29/jungfrau4m_mask-beam.h5
mask_file = /gpfs/cfel/group/cxi/scratch/2021/ESRF-2022-Obertuer-Dec-ID29/mask_old.h5
;mask = /data/mask
mask = /data/data
;mask_good = 0
;mask_bad = 1
mask_good = 0x1
mask_bad = 0x0

;rigid_group_detector = detector
;rigid_group_collection_detector = detector

p1/min_fs = 0
p1/max_fs = 1029
p1/min_ss = 0
p1/max_ss = 513
p1/fs = +1.000000x +0.000000y
p1/ss = -0.000000x +1.000000y
p1/corner_x = -1053.000000
p1/corner_y = -1131.000000

p2/min_fs = 1038
p2/max_fs = 2067
p2/min_ss = 0
p2/max_ss = 513
p2/fs = +1.000000x +0.000000y
p2/ss = -0.000000x +1.000000y
p2/corner_x = -15.000000
p2/corner_y = -1131.000000

p3/min_fs = 0
p3/max_fs = 1029
p3/min_ss = 550
p3/max_ss = 1063
p3/fs = +1.000000x +0.000000y
p3/ss = -0.000000x +1.000000y
p3/corner_x = -1053.000000
p3/corner_y = -581.000000

p4/min_fs = 1038
p4/max_fs = 2067
p4/min_ss = 550
p4/max_ss = 1063
p4/fs = +1.000000x +0.000000y
p4/ss = -0.000000x +1.000000y
p4/corner_x = -15.000000
p4/corner_y = -581.000000

p5/min_fs = 0
p5/max_fs = 1029
p5/min_ss = 1100
p5/max_ss = 1613
p5/fs = +1.000000x +0.000000y
p5/ss = -0.000000x +1.000000y
p5/corner_x = -1053.000000
p5/corner_y = -31.000000

p6/min_fs = 1038
p6/max_fs = 2067
p6/min_ss = 1100
p6/max_ss = 1613
p6/fs = +1.000000x +0.000000y
p6/ss = -0.000000x +1.000000y
p6/corner_x = -15.000000
p6/corner_y = -31.000000

p7/min_fs = 0
p7/max_fs = 1029
p7/min_ss = 1650
p7/max_ss = 2163
p7/fs = +1.000000x +0.000000y
p7/ss = -0.000000x +1.000000y
p7/corner_x = -1053.000000
p7/corner_y = 519.000000

p8/min_fs = 1038
p8/max_fs = 2067
p8/min_ss = 1650
p8/max_ss = 2163
p8/fs = +1.000000x +0.000000y
p8/ss = -0.000000x +1.000000y
p8/corner_x = -15.000000
p8/corner_y = 519.000000


p1/coffset = 0.000000
p2/coffset = 0.000000
p3/coffset = 0.000000
p4/coffset = 0.000000
p5/coffset = 0.000000
p6/coffset = 0.000000
p7/coffset = 0.000000
p8/coffset = 0.000000
