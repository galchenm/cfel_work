adu_per_eV = 0.0075  ; no idea
clen = 0.1249
photon_energy = 9300
res = 5000 ; 200 um pixels

dim0 = %
dim1 = ss
dim2 = fs
;data = /entry_1/instrument_1/detector_1/data
data = /gain/data
;data = /mean/data
;data = /data/data

;mask = /entry_1/instrument_1/detector_1/mask
;mask_good = 0x0000
;mask_bad = 0xfeff


p0/min_fs = 0
p0/min_ss = 0
p0/max_fs = 127
p0/max_ss = 511
p0/fs = +0.000x +1.000y
p0/ss = -1.000x -0.000y
p0/corner_x = 256
p0/corner_y = 64
