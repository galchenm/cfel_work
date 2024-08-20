adu_per_eV = 0.0075  ; no idea
clen = 0.1249
photon_energy = 9300
res = 5000 ; 200 um pixels

dim0 = %
dim1 = ss
dim2 = fs
;data = /entry_1/instrument_1/detector_1/data
;data = /gain/data
;data = /mean/data
data = /data/data

;mask = /entry_1/instrument_1/detector_1/mask
;mask_good = 0x0000
;mask_bad = 0xfeff
mask_file = /gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/detector_signal_correction/subtractedData/shadowMask.h5
mask = /data/data
mask_bad = 0x0000
mask_good = 0x0001

;p0/min_fs = 0
;p0/min_ss = 0
;p0/max_fs = 127
;p0/max_ss = 511
;p0/fs = +0.000x +1.000y
;p0/ss = -1.000x -0.000y
;p0/corner_x = 256
;p0/corner_y = 64

p0a0/min_fs = 0
p0a0/min_ss = 0
p0a0/max_fs = 127
p0a0/max_ss = 63
p0a0/fs = +0.000000x -1.000000y
p0a0/ss = +1.000000x +0.000000y
p0a0/corner_x = -535
p0a0/corner_y = 687

p0a1/min_fs = 0
p0a1/min_ss = 64
p0a1/max_fs = 127
p0a1/max_ss = 127
p0a1/fs = +0.000000x -1.000000y
p0a1/ss = +1.000000x +0.000000y
p0a1/corner_x = -469
p0a1/corner_y = 687

p0a2/min_fs = 0
p0a2/min_ss = 128
p0a2/max_fs = 127
p0a2/max_ss = 191
p0a2/fs = +0.000000x -1.000000y
p0a2/ss = +1.000000x +0.000000y
p0a2/corner_x = -403
p0a2/corner_y = 687

p0a3/min_fs = 0
p0a3/min_ss = 192
p0a3/max_fs = 127
p0a3/max_ss = 255
p0a3/fs = +0.000000x -1.000000y
p0a3/ss = +1.000000x +0.000000y
p0a3/corner_x = -337
p0a3/corner_y = 687

p0a4/min_fs = 0
p0a4/min_ss = 256
p0a4/max_fs = 127
p0a4/max_ss = 319
p0a4/fs = +0.000000x -1.000000y
p0a4/ss = +1.000000x +0.000000y
p0a4/corner_x = -271
p0a4/corner_y = 687

p0a5/min_fs = 0
p0a5/min_ss = 320
p0a5/max_fs = 127
p0a5/max_ss = 383
p0a5/fs = +0.000000x -1.000000y
p0a5/ss = +1.000000x +0.000000y
p0a5/corner_x = -205
p0a5/corner_y = 687

p0a6/min_fs = 0
p0a6/min_ss = 384
p0a6/max_fs = 127
p0a6/max_ss = 447
p0a6/fs = +0.000000x -1.000000y
p0a6/ss = +1.000000x +0.000000y
p0a6/corner_x = -139
p0a6/corner_y = 687

p0a7/min_fs = 0
p0a7/min_ss = 448
p0a7/max_fs = 127
p0a7/max_ss = 511
p0a7/fs = +0.000000x -1.000000y
p0a7/ss = +1.000000x +0.000000y
p0a7/corner_x = -73
p0a7/corner_y = 687
