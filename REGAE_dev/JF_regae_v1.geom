; Optimized panel offsets can be found at the end of the file
; Manually optimized with hdfsee
; Manually optimized with hdfsee
; Manually optimized with hdfsee
; Manually optimized with hdfsee
adu_per_eV = 0.000066  ; 42 adu/keV for highest gain mode
clen = 4.88 ;4.63 ;8.5 ;my - 8.23 ; Ana - 8.7
coffset = 0.000000
photon_energy = 4130000 ; approx! Corresponds to lambda 0.003A - approx.
res = 13333.33
;max_adu = 7500

mask_file = /asap3/fs-bmx/gpfs/regae/2022/data/11015669/processed/yefanov/test/mask_v0.h5 
mask = /data/data
mask_good = 0x01
mask_bad = 0x00

data = /data
;data = /data/data
dim0 = %
dim1 = ss
dim2 = fs

;bad_s0/min_fs = 0
;bad_s0/max_fs = 0
;bad_s0/min_ss = 0
;bad_s0/max_ss = 1023

;bad_s1/min_fs = 255
;bad_s1/max_fs = 256
;bad_s1/min_ss = 0
;bad_s1/max_ss = 1023

;bad_s2/min_fs = 511
;bad_s2/max_fs = 512
;bad_s2/min_ss = 0
;bad_s2/max_ss = 1023

;bad_s3/min_fs = 767
;bad_s3/max_fs = 768
;bad_s3/min_ss = 0
;bad_s3/max_ss = 1023

;bad_s4/min_fs = 1023
;bad_s4/max_fs = 1023
;bad_s4/min_ss = 0
;bad_s4/max_ss = 1023

;bad_m0/min_fs = 0
;bad_m0/max_fs = 1023
;bad_m0/min_ss = 0
;bad_m0/max_ss = 0

;bad_m1/min_fs = 0
;bad_m1/max_fs = 1023
;bad_m1/min_ss = 255
;bad_m1/max_ss = 256

;bad_m2/min_fs = 0
;bad_m2/max_fs = 1023
;bad_m2/min_ss = 511
;bad_m2/max_ss = 512

;bad_m3/min_fs = 0
;bad_m3/max_fs = 1023
;bad_m3/min_ss = 767
;bad_m3/max_ss = 768

;bad_m4/min_fs = 0
;bad_m4/max_fs = 1023
;bad_m4/min_ss = 1023
;bad_m4/max_ss = 1023

rigid_group_p1 = p1a1,p1a2,p1a3,p1a4,p1a5,p1a6,p1a7,p1a8
rigid_group_p2 = p2a1,p2a2,p2a3,p2a4,p2a5,p2a6,p2a7,p2a8
rigid_group_collection_det = p1,p2

p2a1/corner_x = -534.91
p2a1/corner_y = 21.6071
p2a1/fs = +1.000000x -0.000841y
p2a1/ss = +0.000841x +1.000000y
p2a1/min_fs = 0
p2a1/max_fs = 255
p2a1/min_ss = 512
p2a1/max_ss = 767

p2a2/corner_x = -276.91
p2a2/corner_y = 21.3901
p2a2/fs = +1.000000x -0.000841y
p2a2/ss = +0.000841x +1.000000y
p2a2/min_fs = 256
p2a2/max_fs = 511
p2a2/min_ss = 512
p2a2/max_ss = 767

p2a3/corner_x = -18.91
p2a3/corner_y = 21.1731
p2a3/fs = +1.000000x -0.000841y
p2a3/ss = +0.000841x +1.000000y
p2a3/min_fs = 512
p2a3/max_fs = 767
p2a3/min_ss = 512
p2a3/max_ss = 767

p2a4/corner_x = 239.09
p2a4/corner_y = 20.9561
p2a4/fs = +1.000000x -0.000841y
p2a4/ss = +0.000841x +1.000000y
p2a4/min_fs = 768
p2a4/max_fs = 1023
p2a4/min_ss = 512
p2a4/max_ss = 767

p2a5/corner_x = -534.693
p2a5/corner_y = 279.606
p2a5/fs = +1.000000x -0.000841y
p2a5/ss = +0.000841x +1.000000y
p2a5/min_fs = 0
p2a5/max_fs = 255
p2a5/min_ss = 768
p2a5/max_ss = 1023

p2a6/corner_x = -276.693
p2a6/corner_y = 279.39
p2a6/fs = +1.000000x -0.000841y
p2a6/ss = +0.000841x +1.000000y
p2a6/min_fs = 256
p2a6/max_fs = 511
p2a6/min_ss = 768
p2a6/max_ss = 1023

p2a7/corner_x = -18.693
p2a7/corner_y = 279.173
p2a7/fs = +1.000000x -0.000841y
p2a7/ss = +0.000841x +1.000000y
p2a7/min_fs = 512
p2a7/max_fs = 767
p2a7/min_ss = 768
p2a7/max_ss = 1023

p2a8/corner_x = 239.307
p2a8/corner_y = 278.956
p2a8/fs = +1.000000x -0.000841y
p2a8/ss = +0.000841x +1.000000y
p2a8/min_fs = 768
p2a8/max_fs = 1023
p2a8/min_ss = 768
p2a8/max_ss = 1023

p1a1/corner_x = -533.815
p1a1/corner_y = -536.523
p1a1/fs = +1.000000x -0.000641y
p1a1/ss = +0.000641x +1.000000y
p1a1/min_fs = 0
p1a1/max_fs = 255
p1a1/min_ss = 0
p1a1/max_ss = 255

p1a2/corner_x = -275.815
p1a2/corner_y = -536.689
p1a2/fs = +1.000000x -0.000641y
p1a2/ss = +0.000641x +1.000000y
p1a2/min_fs = 256
p1a2/max_fs = 511
p1a2/min_ss = 0
p1a2/max_ss = 255

p1a3/corner_x = -17.815
p1a3/corner_y = -536.854
p1a3/fs = +1.000000x -0.000641y
p1a3/ss = +0.000641x +1.000000y
p1a3/min_fs = 512
p1a3/max_fs = 767
p1a3/min_ss = 0
p1a3/max_ss = 255

p1a4/corner_x = 240.185
p1a4/corner_y = -537.02
p1a4/fs = +1.000000x -0.000641y
p1a4/ss = +0.000641x +1.000000y
p1a4/min_fs = 768
p1a4/max_fs = 1023
p1a4/min_ss = 0
p1a4/max_ss = 255

p1a5/corner_x = -533.649
p1a5/corner_y = -278.523
p1a5/fs = +1.000000x -0.000641y
p1a5/ss = +0.000641x +1.000000y
p1a5/min_fs = 0
p1a5/max_fs = 255
p1a5/min_ss = 256
p1a5/max_ss = 511

p1a6/corner_x = -275.649
p1a6/corner_y = -278.689
p1a6/fs = +1.000000x -0.000641y
p1a6/ss = +0.000641x +1.000000y
p1a6/min_fs = 256
p1a6/max_fs = 511
p1a6/min_ss = 256
p1a6/max_ss = 511

p1a7/corner_x = -17.649
p1a7/corner_y = -278.854
p1a7/fs = +1.000000x -0.000641y
p1a7/ss = +0.000641x +1.000000y
p1a7/min_fs = 512
p1a7/max_fs = 767
p1a7/min_ss = 256
p1a7/max_ss = 511

p1a8/corner_x = 240.351
p1a8/corner_y = -279.02
p1a8/fs = +1.000000x -0.000641y
p1a8/ss = +0.000641x +1.000000y
p1a8/min_fs = 768
p1a8/max_fs = 1023
p1a8/min_ss = 256
p1a8/max_ss = 511

