; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Made of agipd_2480_v5.geom  
; Manually optimized with hdfsee
; OY: this is reasonable for Aug'19 SPB-AGIPD. 4 edge panels are not refined - no data.
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Manually optimized with hdfsee
; Manually optimized with hdfsee
; OY: Made from 2166 experiment. Detector was rebuit !!!!!!!!!!!!!!!!!!!
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Manually optimized with hdfsee
; Manually optimized with hdfsee
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; OY: movement od det by approx. 70mm shited center by 0.3px in both x and y
; OY: After instalation of KB (Sep'18) it looks like the beam is not parall. to the detector rails
; OY: detector center was shifted by -11px in x and -1px in y
; OY: This geometry originated from well callibrated Mar'18 geometry
; OY: I think this is a very well optimized geometry!

adu_per_eV = 0.0075  ; no idea
;clen = 0.210
;clen = 0.3127
clen = 0.1192 ; 0.15
;clen = /CONTROL/SPB_IRU_AGIPD1M/MOTOR/Z_STEPPER/actualPosition/value
;where: h5ls -d /gpfs/exfel/exp/SPB/202001/p002450/proc/r0015/CORR-R0015-DA03-S00000.h5/CONTROL/SPB_IRU_AGIPD1M/MOTOR/Z_STEPPER/actualPosition/value 
;???clen = 0.1425 ; 0.15
;clen = 0.118
;+clen = 0.1248
;clen = 0.164 ;for ADDU=-800
;19.57mm per 100ADDU
photon_energy = 9310
res = 5000 ; 200 um pixels

dim0 = %
;dim2 = ss
;dim3 = fs

;data = /entry_1/instrument_1/detector_1/detector_corrected/data

data = /entry_1/instrument_1/detector_1/data

;data = /entry_1/instrument_1/detector_1/mask


;mask = /entry_1/instrument_1/detector_1/mask
mask = /mask_new/mask
mask_good = 0x0000
mask_bad = 0xfeff


;bad_p7/min_fs = 0
;bad_p7/min_ss = 0
;bad_p7/dim1 = 7
;bad_p7/dim2 = ss 
;bad_p7/dim3 = fs 
;bad_p7/max_fs = 127
;bad_p7/max_ss = 511

;bad_q/min_x = -1000
;bad_q/min_y = 300
;bad_q/max_x = -300
;bad_q/max_y = 1000

rigid_group_q0 = p0a0,p0a1,p0a2,p0a3,p0a4,p0a5,p0a6,p0a7,p1a0,p1a1,p1a2,p1a3,p1a4,p1a5,p1a6,p1a7,p2a0,p2a1,p2a2,p2a3,p2a4,p2a5,p2a6,p2a7,p3a0,p3a1,p3a2,p3a3,p3a4,p3a5,p3a6,p3a7
rigid_group_q1 = p4a0,p4a1,p4a2,p4a3,p4a4,p4a5,p4a6,p4a7,p5a0,p5a1,p5a2,p5a3,p5a4,p5a5,p5a6,p5a7,p6a0,p6a1,p6a2,p6a3,p6a4,p6a5,p6a6,p6a7,p7a0,p7a1,p7a2,p7a3,p7a4,p7a5,p7a6,p7a7
rigid_group_q2 = p8a0,p8a1,p8a2,p8a3,p8a4,p8a5,p8a6,p8a7,p9a0,p9a1,p9a2,p9a3,p9a4,p9a5,p9a6,p9a7,p10a0,p10a1,p10a2,p10a3,p10a4,p10a5,p10a6,p10a7,p11a0,p11a1,p11a2,p11a3,p11a4,p11a5,p11a6,p11a7
rigid_group_q3 = p12a0,p12a1,p12a2,p12a3,p12a4,p12a5,p12a6,p12a7,p13a0,p13a1,p13a2,p13a3,p13a4,p13a5,p13a6,p13a7,p14a0,p14a1,p14a2,p14a3,p14a4,p14a5,p14a6,p14a7,p15a0,p15a1,p15a2,p15a3,p15a4,p15a5,p15a6,p15a7

rigid_group_p0 = p0a0,p0a1,p0a2,p0a3,p0a4,p0a5,p0a6,p0a7
rigid_group_p1 = p1a0,p1a1,p1a2,p1a3,p1a4,p1a5,p1a6,p1a7
rigid_group_p2 = p2a0,p2a1,p2a2,p2a3,p2a4,p2a5,p2a6,p2a7
rigid_group_p3 = p3a0,p3a1,p3a2,p3a3,p3a4,p3a5,p3a6,p3a7
rigid_group_p4 = p4a0,p4a1,p4a2,p4a3,p4a4,p4a5,p4a6,p4a7
rigid_group_p5 = p5a0,p5a1,p5a2,p5a3,p5a4,p5a5,p5a6,p5a7
rigid_group_p6 = p6a0,p6a1,p6a2,p6a3,p6a4,p6a5,p6a6,p6a7
rigid_group_p7 = p7a0,p7a1,p7a2,p7a3,p7a4,p7a5,p7a6,p7a7
rigid_group_p8 = p8a0,p8a1,p8a2,p8a3,p8a4,p8a5,p8a6,p8a7
rigid_group_p9 = p9a0,p9a1,p9a2,p9a3,p9a4,p9a5,p9a6,p9a7
rigid_group_p10 = p10a0,p10a1,p10a2,p10a3,p10a4,p10a5,p10a6,p10a7
rigid_group_p11 = p11a0,p11a1,p11a2,p11a3,p11a4,p11a5,p11a6,p11a7
rigid_group_p12 = p12a0,p12a1,p12a2,p12a3,p12a4,p12a5,p12a6,p12a7
rigid_group_p13 = p13a0,p13a1,p13a2,p13a3,p13a4,p13a5,p13a6,p13a7
rigid_group_p14 = p14a0,p14a1,p14a2,p14a3,p14a4,p14a5,p14a6,p14a7
rigid_group_p15 = p15a0,p15a1,p15a2,p15a3,p15a4,p15a5,p15a6,p15a7

rigid_group_collection_quadrants = q0,q1,q2,q3
rigid_group_collection_asics = p0,p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15

p0a0/min_fs = 0
p0a0/min_ss = 0
p0a0/max_fs = 127
p0a0/max_ss = 63
p0a0/fs = -0.002466x -0.999993y
p0a0/ss = +0.999993x -0.002466y
p0a0/corner_x = -520.282
p0a0/corner_y = 632.995

p0a1/min_fs = 0
p0a1/min_ss = 64
p0a1/max_fs = 127
p0a1/max_ss = 127
p0a1/fs = -0.002466x -0.999993y
p0a1/ss = +0.999993x -0.002466y
p0a1/corner_x = -454.282
p0a1/corner_y = 632.811

p0a2/min_fs = 0
p0a2/min_ss = 128
p0a2/max_fs = 127
p0a2/max_ss = 191
p0a2/fs = -0.002466x -0.999993y
p0a2/ss = +0.999993x -0.002466y
p0a2/corner_x = -388.288
p0a2/corner_y = 632.627

p0a3/min_fs = 0
p0a3/min_ss = 192
p0a3/max_fs = 127
p0a3/max_ss = 255
p0a3/fs = -0.002466x -0.999993y
p0a3/ss = +0.999993x -0.002466y
p0a3/corner_x = -322.287
p0a3/corner_y = 632.441

p0a4/min_fs = 0
p0a4/min_ss = 256
p0a4/max_fs = 127
p0a4/max_ss = 319
p0a4/fs = -0.002466x -0.999993y
p0a4/ss = +0.999993x -0.002466y
p0a4/corner_x = -256.288
p0a4/corner_y = 632.256

p0a5/min_fs = 0
p0a5/min_ss = 320
p0a5/max_fs = 127
p0a5/max_ss = 383
p0a5/fs = -0.002466x -0.999993y
p0a5/ss = +0.999993x -0.002466y
p0a5/corner_x = -190.286
p0a5/corner_y = 632.181

p0a6/min_fs = 0
p0a6/min_ss = 384
p0a6/max_fs = 127
p0a6/max_ss = 447
p0a6/fs = -0.002466x -0.999993y
p0a6/ss = +0.999993x -0.002466y
p0a6/corner_x = -124.286
p0a6/corner_y = 632.019

p0a7/min_fs = 0
p0a7/min_ss = 448
p0a7/max_fs = 127
p0a7/max_ss = 511
p0a7/fs = -0.002466x -0.999993y
p0a7/ss = +0.999993x -0.002466y
p0a7/corner_x = -58.2862
p0a7/corner_y = 631.856

p1a0/min_fs = 0
p1a0/min_ss = 0
p1a0/max_fs = 127
p1a0/max_ss = 63
p1a0/fs = -0.002362x -0.999998y
p1a0/ss = +0.999998x -0.002362y
p1a0/corner_x = -520.608
p1a0/corner_y = 474.78

p1a1/min_fs = 0
p1a1/min_ss = 64
p1a1/max_fs = 127
p1a1/max_ss = 127
p1a1/fs = -0.002362x -0.999998y
p1a1/ss = +0.999998x -0.002362y
p1a1/corner_x = -454.61
p1a1/corner_y = 474.638

p1a2/min_fs = 0
p1a2/min_ss = 128
p1a2/max_fs = 127
p1a2/max_ss = 191
p1a2/fs = -0.002362x -0.999998y
p1a2/ss = +0.999998x -0.002362y
p1a2/corner_x = -388.612
p1a2/corner_y = 474.492

p1a3/min_fs = 0
p1a3/min_ss = 192
p1a3/max_fs = 127
p1a3/max_ss = 255
p1a3/fs = -0.002362x -0.999998y
p1a3/ss = +0.999998x -0.002362y
p1a3/corner_x = -322.615
p1a3/corner_y = 474.348

p1a4/min_fs = 0
p1a4/min_ss = 256
p1a4/max_fs = 127
p1a4/max_ss = 319
p1a4/fs = -0.002362x -0.999998y
p1a4/ss = +0.999998x -0.002362y
p1a4/corner_x = -256.616
p1a4/corner_y = 474.207

p1a5/min_fs = 0
p1a5/min_ss = 320
p1a5/max_fs = 127
p1a5/max_ss = 383
p1a5/fs = -0.002362x -0.999998y
p1a5/ss = +0.999998x -0.002362y
p1a5/corner_x = -190.619
p1a5/corner_y = 474.06

p1a6/min_fs = 0
p1a6/min_ss = 384
p1a6/max_fs = 127
p1a6/max_ss = 447
p1a6/fs = -0.002362x -0.999998y
p1a6/ss = +0.999998x -0.002362y
p1a6/corner_x = -124.604
p1a6/corner_y = 473.916

p1a7/min_fs = 0
p1a7/min_ss = 448
p1a7/max_fs = 127
p1a7/max_ss = 511
p1a7/fs = -0.002362x -0.999998y
p1a7/ss = +0.999998x -0.002362y
p1a7/corner_x = -58.6035
p1a7/corner_y = 473.773

p2a0/min_fs = 0
p2a0/min_ss = 0
p2a0/max_fs = 127
p2a0/max_ss = 63
p2a0/fs = -0.000208x -1.000001y
p2a0/ss = +1.000001x -0.000208y
p2a0/corner_x = -520.744
p2a0/corner_y = 317.82

p2a1/min_fs = 0
p2a1/min_ss = 64
p2a1/max_fs = 127
p2a1/max_ss = 127
p2a1/fs = -0.000208x -1.000001y
p2a1/ss = +1.000001x -0.000208y
p2a1/corner_x = -454.745
p2a1/corner_y = 317.799

p2a2/min_fs = 0
p2a2/min_ss = 128
p2a2/max_fs = 127
p2a2/max_ss = 191
p2a2/fs = -0.000208x -1.000001y
p2a2/ss = +1.000001x -0.000208y
p2a2/corner_x = -388.746
p2a2/corner_y = 317.777

p2a3/min_fs = 0
p2a3/min_ss = 192
p2a3/max_fs = 127
p2a3/max_ss = 255
p2a3/fs = -0.000208x -1.000001y
p2a3/ss = +1.000001x -0.000208y
p2a3/corner_x = -322.746
p2a3/corner_y = 317.754

p2a4/min_fs = 0
p2a4/min_ss = 256
p2a4/max_fs = 127
p2a4/max_ss = 319
p2a4/fs = -0.000208x -1.000001y
p2a4/ss = +1.000001x -0.000208y
p2a4/corner_x = -256.747
p2a4/corner_y = 317.731

p2a5/min_fs = 0
p2a5/min_ss = 320
p2a5/max_fs = 127
p2a5/max_ss = 383
p2a5/fs = -0.000208x -1.000001y
p2a5/ss = +1.000001x -0.000208y
p2a5/corner_x = -190.75
p2a5/corner_y = 317.712

p2a6/min_fs = 0
p2a6/min_ss = 384
p2a6/max_fs = 127
p2a6/max_ss = 447
p2a6/fs = -0.000208x -1.000001y
p2a6/ss = +1.000001x -0.000208y
p2a6/corner_x = -124.735
p2a6/corner_y = 317.687

p2a7/min_fs = 0
p2a7/min_ss = 448
p2a7/max_fs = 127
p2a7/max_ss = 511
p2a7/fs = -0.000208x -1.000001y
p2a7/ss = +1.000001x -0.000208y
p2a7/corner_x = -58.7319
p2a7/corner_y = 317.665

p3a0/min_fs = 0
p3a0/min_ss = 0
p3a0/max_fs = 127
p3a0/max_ss = 63
p3a0/fs = +0.000896x -0.999999y
p3a0/ss = +0.999999x +0.000896y
p3a0/corner_x = -521.111
p3a0/corner_y = 159.729

p3a1/min_fs = 0
p3a1/min_ss = 64
p3a1/max_fs = 127
p3a1/max_ss = 127
p3a1/fs = +0.000896x -0.999999y
p3a1/ss = +0.999999x +0.000896y
p3a1/corner_x = -455.115
p3a1/corner_y = 159.792

p3a2/min_fs = 0
p3a2/min_ss = 128
p3a2/max_fs = 127
p3a2/max_ss = 191
p3a2/fs = +0.000896x -0.999999y
p3a2/ss = +0.999999x +0.000896y
p3a2/corner_x = -389.116
p3a2/corner_y = 159.852

p3a3/min_fs = 0
p3a3/min_ss = 192
p3a3/max_fs = 127
p3a3/max_ss = 255
p3a3/fs = +0.000896x -0.999999y
p3a3/ss = +0.999999x +0.000896y
p3a3/corner_x = -323.119
p3a3/corner_y = 159.912

p3a4/min_fs = 0
p3a4/min_ss = 256
p3a4/max_fs = 127
p3a4/max_ss = 319
p3a4/fs = +0.000896x -0.999999y
p3a4/ss = +0.999999x +0.000896y
p3a4/corner_x = -257.12
p3a4/corner_y = 159.972

p3a5/min_fs = 0
p3a5/min_ss = 320
p3a5/max_fs = 127
p3a5/max_ss = 383
p3a5/fs = +0.000896x -0.999999y
p3a5/ss = +0.999999x +0.000896y
p3a5/corner_x = -191.105
p3a5/corner_y = 160.033

p3a6/min_fs = 0
p3a6/min_ss = 384
p3a6/max_fs = 127
p3a6/max_ss = 447
p3a6/fs = +0.000896x -0.999999y
p3a6/ss = +0.999999x +0.000896y
p3a6/corner_x = -125.104
p3a6/corner_y = 160.095

p3a7/min_fs = 0
p3a7/min_ss = 448
p3a7/max_fs = 127
p3a7/max_ss = 511
p3a7/fs = +0.000896x -0.999999y
p3a7/ss = +0.999999x +0.000896y
p3a7/corner_x = -59.1023
p3a7/corner_y = 160.156

p4a0/min_fs = 0
p4a0/min_ss = 0
p4a0/max_fs = 127
p4a0/max_ss = 63
p4a0/fs = -0.000745x -1.000001y
p4a0/ss = +1.000001x -0.000745y
p4a0/corner_x = -555.344
p4a0/corner_y = -2.87537

p4a1/min_fs = 0
p4a1/min_ss = 64
p4a1/max_fs = 127
p4a1/max_ss = 127
p4a1/fs = -0.000745x -1.000001y
p4a1/ss = +1.000001x -0.000745y
p4a1/corner_x = -489.348
p4a1/corner_y = -2.91613

p4a2/min_fs = 0
p4a2/min_ss = 128
p4a2/max_fs = 127
p4a2/max_ss = 191
p4a2/fs = -0.000745x -1.000001y
p4a2/ss = +1.000001x -0.000745y
p4a2/corner_x = -423.35
p4a2/corner_y = -2.957

p4a3/min_fs = 0
p4a3/min_ss = 192
p4a3/max_fs = 127
p4a3/max_ss = 255
p4a3/fs = -0.000745x -1.000001y
p4a3/ss = +1.000001x -0.000745y
p4a3/corner_x = -357.353
p4a3/corner_y = -2.99785

p4a4/min_fs = 0
p4a4/min_ss = 256
p4a4/max_fs = 127
p4a4/max_ss = 319
p4a4/fs = -0.000745x -1.000001y
p4a4/ss = +1.000001x -0.000745y
p4a4/corner_x = -291.354
p4a4/corner_y = -3.03869

p4a5/min_fs = 0
p4a5/min_ss = 320
p4a5/max_fs = 127
p4a5/max_ss = 383
p4a5/fs = -0.000745x -1.000001y
p4a5/ss = +1.000001x -0.000745y
p4a5/corner_x = -225.356
p4a5/corner_y = -3.07957

p4a6/min_fs = 0
p4a6/min_ss = 384
p4a6/max_fs = 127
p4a6/max_ss = 447
p4a6/fs = -0.000745x -1.000001y
p4a6/ss = +1.000001x -0.000745y
p4a6/corner_x = -159.358
p4a6/corner_y = -3.12033

p4a7/min_fs = 0
p4a7/min_ss = 448
p4a7/max_fs = 127
p4a7/max_ss = 511
p4a7/fs = -0.000745x -1.000001y
p4a7/ss = +1.000001x -0.000745y
p4a7/corner_x = -93.3623
p4a7/corner_y = -3.16128

p5a0/min_fs = 0
p5a0/min_ss = 0
p5a0/max_fs = 127
p5a0/max_ss = 63
p5a0/fs = +0.001273x -0.999999y
p5a0/ss = +0.999999x +0.001273y
p5a0/corner_x = -555.584
p5a0/corner_y = -161.532

p5a1/min_fs = 0
p5a1/min_ss = 64
p5a1/max_fs = 127
p5a1/max_ss = 127
p5a1/fs = +0.001273x -0.999999y
p5a1/ss = +0.999999x +0.001273y
p5a1/corner_x = -489.587
p5a1/corner_y = -161.453

p5a2/min_fs = 0
p5a2/min_ss = 128
p5a2/max_fs = 127
p5a2/max_ss = 191
p5a2/fs = +0.001273x -0.999999y
p5a2/ss = +0.999999x +0.001273y
p5a2/corner_x = -423.589
p5a2/corner_y = -161.378

p5a3/min_fs = 0
p5a3/min_ss = 192
p5a3/max_fs = 127
p5a3/max_ss = 255
p5a3/fs = +0.001273x -0.999999y
p5a3/ss = +0.999999x +0.001273y
p5a3/corner_x = -357.591
p5a3/corner_y = -161.302

p5a4/min_fs = 0
p5a4/min_ss = 256
p5a4/max_fs = 127
p5a4/max_ss = 319
p5a4/fs = +0.001273x -0.999999y
p5a4/ss = +0.999999x +0.001273y
p5a4/corner_x = -291.593
p5a4/corner_y = -161.225

p5a5/min_fs = 0
p5a5/min_ss = 320
p5a5/max_fs = 127
p5a5/max_ss = 383
p5a5/fs = +0.001273x -0.999999y
p5a5/ss = +0.999999x +0.001273y
p5a5/corner_x = -225.578
p5a5/corner_y = -161.15

p5a6/min_fs = 0
p5a6/min_ss = 384
p5a6/max_fs = 127
p5a6/max_ss = 447
p5a6/fs = +0.001273x -0.999999y
p5a6/ss = +0.999999x +0.001273y
p5a6/corner_x = -159.578
p5a6/corner_y = -161.073

p5a7/min_fs = 0
p5a7/min_ss = 448
p5a7/max_fs = 127
p5a7/max_ss = 511
p5a7/fs = +0.001273x -0.999999y
p5a7/ss = +0.999999x +0.001273y
p5a7/corner_x = -93.5777
p5a7/corner_y = -160.996

p6a0/min_fs = 0
p6a0/min_ss = 0
p6a0/max_fs = 127
p6a0/max_ss = 63
p6a0/fs = -0.002609x -0.999998y
p6a0/ss = +0.999998x -0.002609y
p6a0/corner_x = -555.484
p6a0/corner_y = -317.105

p6a1/min_fs = 0
p6a1/min_ss = 64
p6a1/max_fs = 127
p6a1/max_ss = 127
p6a1/fs = -0.002609x -0.999998y
p6a1/ss = +0.999998x -0.002609y
p6a1/corner_x = -489.486
p6a1/corner_y = -317.281

p6a2/min_fs = 0
p6a2/min_ss = 128
p6a2/max_fs = 127
p6a2/max_ss = 191
p6a2/fs = -0.002609x -0.999998y
p6a2/ss = +0.999998x -0.002609y
p6a2/corner_x = -423.489
p6a2/corner_y = -317.465

p6a3/min_fs = 0
p6a3/min_ss = 192
p6a3/max_fs = 127
p6a3/max_ss = 255
p6a3/fs = -0.002609x -0.999998y
p6a3/ss = +0.999998x -0.002609y
p6a3/corner_x = -357.492
p6a3/corner_y = -317.645

p6a4/min_fs = 0
p6a4/min_ss = 256
p6a4/max_fs = 127
p6a4/max_ss = 319
p6a4/fs = -0.002609x -0.999998y
p6a4/ss = +0.999998x -0.002609y
p6a4/corner_x = -291.496
p6a4/corner_y = -317.826

p6a5/min_fs = 0
p6a5/min_ss = 320
p6a5/max_fs = 127
p6a5/max_ss = 383
p6a5/fs = -0.002609x -0.999998y
p6a5/ss = +0.999998x -0.002609y
p6a5/corner_x = -225.497
p6a5/corner_y = -318.008

p6a6/min_fs = 0
p6a6/min_ss = 384
p6a6/max_fs = 127
p6a6/max_ss = 447
p6a6/fs = -0.002609x -0.999998y
p6a6/ss = +0.999998x -0.002609y
p6a6/corner_x = -159.5
p6a6/corner_y = -318.189

p6a7/min_fs = 0
p6a7/min_ss = 448
p6a7/max_fs = 127
p6a7/max_ss = 511
p6a7/fs = -0.002609x -0.999998y
p6a7/ss = +0.999998x -0.002609y
p6a7/corner_x = -93.5009
p6a7/corner_y = -318.369

p7a0/min_fs = 0
p7a0/min_ss = 0
p7a0/max_fs = 127
p7a0/max_ss = 63
p7a0/fs = -0.001177x -0.999998y
p7a0/ss = +0.999998x -0.001177y
p7a0/corner_x = -554.68
p7a0/corner_y = -475.381

p7a1/min_fs = 0
p7a1/min_ss = 64
p7a1/max_fs = 127
p7a1/max_ss = 127
p7a1/fs = -0.001177x -0.999998y
p7a1/ss = +0.999998x -0.001177y
p7a1/corner_x = -488.686
p7a1/corner_y = -475.458

p7a2/min_fs = 0
p7a2/min_ss = 128
p7a2/max_fs = 127
p7a2/max_ss = 191
p7a2/fs = -0.001177x -0.999998y
p7a2/ss = +0.999998x -0.001177y
p7a2/corner_x = -422.69
p7a2/corner_y = -475.54

p7a3/min_fs = 0
p7a3/min_ss = 192
p7a3/max_fs = 127
p7a3/max_ss = 255
p7a3/fs = -0.001177x -0.999998y
p7a3/ss = +0.999998x -0.001177y
p7a3/corner_x = -356.692
p7a3/corner_y = -475.622

p7a4/min_fs = 0
p7a4/min_ss = 256
p7a4/max_fs = 127
p7a4/max_ss = 319
p7a4/fs = -0.001177x -0.999998y
p7a4/ss = +0.999998x -0.001177y
p7a4/corner_x = -290.696
p7a4/corner_y = -475.701

p7a5/min_fs = 0
p7a5/min_ss = 320
p7a5/max_fs = 127
p7a5/max_ss = 383
p7a5/fs = -0.001177x -0.999998y
p7a5/ss = +0.999998x -0.001177y
p7a5/corner_x = -224.699
p7a5/corner_y = -475.783

p7a6/min_fs = 0
p7a6/min_ss = 384
p7a6/max_fs = 127
p7a6/max_ss = 447
p7a6/fs = -0.001177x -0.999998y
p7a6/ss = +0.999998x -0.001177y
p7a6/corner_x = -158.7
p7a6/corner_y = -475.862

p7a7/min_fs = 0
p7a7/min_ss = 448
p7a7/max_fs = 127
p7a7/max_ss = 511
p7a7/fs = -0.001177x -0.999998y
p7a7/ss = +0.999998x -0.001177y
p7a7/corner_x = -92.7039
p7a7/corner_y = -475.941

p8a0/min_fs = 0
p8a0/min_ss = 0
p8a0/max_fs = 127
p8a0/max_ss = 63
p8a0/fs = -0.000960x +0.999999y
p8a0/ss = -0.999999x -0.000960y
p8a0/corner_x = 515.434
p8a0/corner_y = -162.894

p8a1/min_fs = 0
p8a1/min_ss = 64
p8a1/max_fs = 127
p8a1/max_ss = 127
p8a1/fs = -0.000960x +0.999999y
p8a1/ss = -0.999999x -0.000960y
p8a1/corner_x = 449.436
p8a1/corner_y = -162.962

p8a2/min_fs = 0
p8a2/min_ss = 128
p8a2/max_fs = 127
p8a2/max_ss = 191
p8a2/fs = -0.000960x +0.999999y
p8a2/ss = -0.999999x -0.000960y
p8a2/corner_x = 383.437
p8a2/corner_y = -163.029

p8a3/min_fs = 0
p8a3/min_ss = 192
p8a3/max_fs = 127
p8a3/max_ss = 255
p8a3/fs = -0.000960x +0.999999y
p8a3/ss = -0.999999x -0.000960y
p8a3/corner_x = 317.44
p8a3/corner_y = -163.099

p8a4/min_fs = 0
p8a4/min_ss = 256
p8a4/max_fs = 127
p8a4/max_ss = 319
p8a4/fs = -0.000960x +0.999999y
p8a4/ss = -0.999999x -0.000960y
p8a4/corner_x = 251.442
p8a4/corner_y = -163.165

p8a5/min_fs = 0
p8a5/min_ss = 320
p8a5/max_fs = 127
p8a5/max_ss = 383
p8a5/fs = -0.000960x +0.999999y
p8a5/ss = -0.999999x -0.000960y
p8a5/corner_x = 185.443
p8a5/corner_y = -163.236

p8a6/min_fs = 0
p8a6/min_ss = 384
p8a6/max_fs = 127
p8a6/max_ss = 447
p8a6/fs = -0.000960x +0.999999y
p8a6/ss = -0.999999x -0.000960y
p8a6/corner_x = 119.446
p8a6/corner_y = -163.303

p8a7/min_fs = 0
p8a7/min_ss = 448
p8a7/max_fs = 127
p8a7/max_ss = 511
p8a7/fs = -0.000960x +0.999999y
p8a7/ss = -0.999999x -0.000960y
p8a7/corner_x = 53.4481
p8a7/corner_y = -163.372

p9a0/min_fs = 0
p9a0/min_ss = 0
p9a0/max_fs = 127
p9a0/max_ss = 63
p9a0/fs = -0.000749x +1.000000y
p9a0/ss = -1.000000x -0.000749y
p9a0/corner_x = 515.384
p9a0/corner_y = -320.125

p9a1/min_fs = 0
p9a1/min_ss = 64
p9a1/max_fs = 127
p9a1/max_ss = 127
p9a1/fs = -0.000749x +1.000000y
p9a1/ss = -1.000000x -0.000749y
p9a1/corner_x = 449.387
p9a1/corner_y = -320.178

p9a2/min_fs = 0
p9a2/min_ss = 128
p9a2/max_fs = 127
p9a2/max_ss = 191
p9a2/fs = -0.000749x +1.000000y
p9a2/ss = -1.000000x -0.000749y
p9a2/corner_x = 383.39
p9a2/corner_y = -320.232

p9a3/min_fs = 0
p9a3/min_ss = 192
p9a3/max_fs = 127
p9a3/max_ss = 255
p9a3/fs = -0.000749x +1.000000y
p9a3/ss = -1.000000x -0.000749y
p9a3/corner_x = 317.393
p9a3/corner_y = -320.284

p9a4/min_fs = 0
p9a4/min_ss = 256
p9a4/max_fs = 127
p9a4/max_ss = 319
p9a4/fs = -0.000749x +1.000000y
p9a4/ss = -1.000000x -0.000749y
p9a4/corner_x = 251.395
p9a4/corner_y = -320.336

p9a5/min_fs = 0
p9a5/min_ss = 320
p9a5/max_fs = 127
p9a5/max_ss = 383
p9a5/fs = -0.000749x +1.000000y
p9a5/ss = -1.000000x -0.000749y
p9a5/corner_x = 185.398
p9a5/corner_y = -320.391

p9a6/min_fs = 0
p9a6/min_ss = 384
p9a6/max_fs = 127
p9a6/max_ss = 447
p9a6/fs = -0.000749x +1.000000y
p9a6/ss = -1.000000x -0.000749y
p9a6/corner_x = 119.379
p9a6/corner_y = -320.442

p9a7/min_fs = 0
p9a7/min_ss = 448
p9a7/max_fs = 127
p9a7/max_ss = 511
p9a7/fs = -0.000749x +1.000000y
p9a7/ss = -1.000000x -0.000749y
p9a7/corner_x = 53.3771
p9a7/corner_y = -320.495

p10a0/min_fs = 0
p10a0/min_ss = 0
p10a0/max_fs = 127
p10a0/max_ss = 63
p10a0/fs = -0.001601x +0.999997y
p10a0/ss = -0.999997x -0.001601y
p10a0/corner_x = 515.471
p10a0/corner_y = -476.965

p10a1/min_fs = 0
p10a1/min_ss = 64
p10a1/max_fs = 127
p10a1/max_ss = 127
p10a1/fs = -0.001601x +0.999997y
p10a1/ss = -0.999997x -0.001601y
p10a1/corner_x = 449.475
p10a1/corner_y = -477.081

p10a2/min_fs = 0
p10a2/min_ss = 128
p10a2/max_fs = 127
p10a2/max_ss = 191
p10a2/fs = -0.001601x +0.999997y
p10a2/ss = -0.999997x -0.001601y
p10a2/corner_x = 383.478
p10a2/corner_y = -477.195

p10a3/min_fs = 0
p10a3/min_ss = 192
p10a3/max_fs = 127
p10a3/max_ss = 255
p10a3/fs = -0.001601x +0.999997y
p10a3/ss = -0.999997x -0.001601y
p10a3/corner_x = 317.482
p10a3/corner_y = -477.31

p10a4/min_fs = 0
p10a4/min_ss = 256
p10a4/max_fs = 127
p10a4/max_ss = 319
p10a4/fs = -0.001601x +0.999997y
p10a4/ss = -0.999997x -0.001601y
p10a4/corner_x = 251.485
p10a4/corner_y = -477.422

p10a5/min_fs = 0
p10a5/min_ss = 320
p10a5/max_fs = 127
p10a5/max_ss = 383
p10a5/fs = -0.001601x +0.999997y
p10a5/ss = -0.999997x -0.001601y
p10a5/corner_x = 185.487
p10a5/corner_y = -477.538

p10a6/min_fs = 0
p10a6/min_ss = 384
p10a6/max_fs = 127
p10a6/max_ss = 447
p10a6/fs = -0.001601x +0.999997y
p10a6/ss = -0.999997x -0.001601y
p10a6/corner_x = 119.491
p10a6/corner_y = -477.653

p10a7/min_fs = 0
p10a7/min_ss = 448
p10a7/max_fs = 127
p10a7/max_ss = 511
p10a7/fs = -0.001601x +0.999997y
p10a7/ss = -0.999997x -0.001601y
p10a7/corner_x = 53.4926
p10a7/corner_y = -477.767

p11a0/min_fs = 0
p11a0/min_ss = 0
p11a0/max_fs = 127
p11a0/max_ss = 63
p11a0/fs = -0.003484x +0.999994y
p11a0/ss = -0.999994x -0.003484y
p11a0/corner_x = 515.895
p11a0/corner_y = -634.451

p11a1/min_fs = 0
p11a1/min_ss = 64
p11a1/max_fs = 127
p11a1/max_ss = 127
p11a1/fs = -0.003484x +0.999994y
p11a1/ss = -0.999994x -0.003484y
p11a1/corner_x = 449.894
p11a1/corner_y = -634.687

p11a2/min_fs = 0
p11a2/min_ss = 128
p11a2/max_fs = 127
p11a2/max_ss = 191
p11a2/fs = -0.003484x +0.999994y
p11a2/ss = -0.999994x -0.003484y
p11a2/corner_x = 383.898
p11a2/corner_y = -634.923

p11a3/min_fs = 0
p11a3/min_ss = 192
p11a3/max_fs = 127
p11a3/max_ss = 255
p11a3/fs = -0.003484x +0.999994y
p11a3/ss = -0.999994x -0.003484y
p11a3/corner_x = 317.9
p11a3/corner_y = -635.159

p11a4/min_fs = 0
p11a4/min_ss = 256
p11a4/max_fs = 127
p11a4/max_ss = 319
p11a4/fs = -0.003484x +0.999994y
p11a4/ss = -0.999994x -0.003484y
p11a4/corner_x = 251.906
p11a4/corner_y = -635.394

p11a5/min_fs = 0
p11a5/min_ss = 320
p11a5/max_fs = 127
p11a5/max_ss = 383
p11a5/fs = -0.003484x +0.999994y
p11a5/ss = -0.999994x -0.003484y
p11a5/corner_x = 185.907
p11a5/corner_y = -635.632

p11a6/min_fs = 0
p11a6/min_ss = 384
p11a6/max_fs = 127
p11a6/max_ss = 447
p11a6/fs = -0.003484x +0.999994y
p11a6/ss = -0.999994x -0.003484y
p11a6/corner_x = 119.912
p11a6/corner_y = -635.866

p11a7/min_fs = 0
p11a7/min_ss = 448
p11a7/max_fs = 127
p11a7/max_ss = 511
p11a7/fs = -0.003484x +0.999994y
p11a7/ss = -0.999994x -0.003484y
p11a7/corner_x = 53.9119
p11a7/corner_y = -636.103

p12a0/min_fs = 0
p12a0/min_ss = 0
p12a0/max_fs = 127
p12a0/max_ss = 63
p12a0/fs = -0.001442x +1.000000y
p12a0/ss = -1.000000x -0.001442y
p12a0/corner_x = 548.628
p12a0/corner_y = 469.509

p12a1/min_fs = 0
p12a1/min_ss = 64
p12a1/max_fs = 127
p12a1/max_ss = 127
p12a1/fs = -0.001442x +1.000000y
p12a1/ss = -1.000000x -0.001442y
p12a1/corner_x = 482.629
p12a1/corner_y = 469.366

p12a2/min_fs = 0
p12a2/min_ss = 128
p12a2/max_fs = 127
p12a2/max_ss = 191
p12a2/fs = -0.001442x +1.000000y
p12a2/ss = -1.000000x -0.001442y
p12a2/corner_x = 416.633
p12a2/corner_y = 469.224

p12a3/min_fs = 0
p12a3/min_ss = 192
p12a3/max_fs = 127
p12a3/max_ss = 255
p12a3/fs = -0.001442x +1.000000y
p12a3/ss = -1.000000x -0.001442y
p12a3/corner_x = 350.629
p12a3/corner_y = 469.223

p12a4/min_fs = 0
p12a4/min_ss = 256
p12a4/max_fs = 127
p12a4/max_ss = 319
p12a4/fs = -0.001442x +1.000000y
p12a4/ss = -1.000000x -0.001442y
p12a4/corner_x = 284.628
p12a4/corner_y = 469.127

p12a5/min_fs = 0
p12a5/min_ss = 320
p12a5/max_fs = 127
p12a5/max_ss = 383
p12a5/fs = -0.001442x +1.000000y
p12a5/ss = -1.000000x -0.001442y
p12a5/corner_x = 218.628
p12a5/corner_y = 469.031

p12a6/min_fs = 0
p12a6/min_ss = 384
p12a6/max_fs = 127
p12a6/max_ss = 447
p12a6/fs = -0.001442x +1.000000y
p12a6/ss = -1.000000x -0.001442y
p12a6/corner_x = 152.629
p12a6/corner_y = 468.936

p12a7/min_fs = 0
p12a7/min_ss = 448
p12a7/max_fs = 127
p12a7/max_ss = 511
p12a7/fs = -0.001442x +1.000000y
p12a7/ss = -1.000000x -0.001442y
p12a7/corner_x = 86.6277
p12a7/corner_y = 468.84

p13a0/min_fs = 0
p13a0/min_ss = 0
p13a0/max_fs = 127
p13a0/max_ss = 63
p13a0/fs = +0.000666x +1.000000y
p13a0/ss = -1.000000x +0.000666y
p13a0/corner_x = 547.92
p13a0/corner_y = 311.47

p13a1/min_fs = 0
p13a1/min_ss = 64
p13a1/max_fs = 127
p13a1/max_ss = 127
p13a1/fs = +0.000666x +1.000000y
p13a1/ss = -1.000000x +0.000666y
p13a1/corner_x = 481.921
p13a1/corner_y = 311.5

p13a2/min_fs = 0
p13a2/min_ss = 128
p13a2/max_fs = 127
p13a2/max_ss = 191
p13a2/fs = +0.000666x +1.000000y
p13a2/ss = -1.000000x +0.000666y
p13a2/corner_x = 415.926
p13a2/corner_y = 311.534

p13a3/min_fs = 0
p13a3/min_ss = 192
p13a3/max_fs = 127
p13a3/max_ss = 255
p13a3/fs = +0.000666x +1.000000y
p13a3/ss = -1.000000x +0.000666y
p13a3/corner_x = 349.929
p13a3/corner_y = 311.566

p13a4/min_fs = 0
p13a4/min_ss = 256
p13a4/max_fs = 127
p13a4/max_ss = 319
p13a4/fs = +0.000666x +1.000000y
p13a4/ss = -1.000000x +0.000666y
p13a4/corner_x = 283.932
p13a4/corner_y = 311.597

p13a5/min_fs = 0
p13a5/min_ss = 320
p13a5/max_fs = 127
p13a5/max_ss = 383
p13a5/fs = +0.000666x +1.000000y
p13a5/ss = -1.000000x +0.000666y
p13a5/corner_x = 217.917
p13a5/corner_y = 311.629

p13a6/min_fs = 0
p13a6/min_ss = 384
p13a6/max_fs = 127
p13a6/max_ss = 447
p13a6/fs = +0.000666x +1.000000y
p13a6/ss = -1.000000x +0.000666y
p13a6/corner_x = 151.916
p13a6/corner_y = 311.664

p13a7/min_fs = 0
p13a7/min_ss = 448
p13a7/max_fs = 127
p13a7/max_ss = 511
p13a7/fs = +0.000666x +1.000000y
p13a7/ss = -1.000000x +0.000666y
p13a7/corner_x = 85.9162
p13a7/corner_y = 311.694

p14a0/min_fs = 0
p14a0/min_ss = 0
p14a0/max_fs = 127
p14a0/max_ss = 63
p14a0/fs = -0.001319x +1.000000y
p14a0/ss = -1.000000x -0.001319y
p14a0/corner_x = 549.24
p14a0/corner_y = 155.136

p14a1/min_fs = 0
p14a1/min_ss = 64
p14a1/max_fs = 127
p14a1/max_ss = 127
p14a1/fs = -0.001319x +1.000000y
p14a1/ss = -1.000000x -0.001319y
p14a1/corner_x = 483.242
p14a1/corner_y = 155.045

p14a2/min_fs = 0
p14a2/min_ss = 128
p14a2/max_fs = 127
p14a2/max_ss = 191
p14a2/fs = -0.001319x +1.000000y
p14a2/ss = -1.000000x -0.001319y
p14a2/corner_x = 417.246
p14a2/corner_y = 154.955

p14a3/min_fs = 0
p14a3/min_ss = 192
p14a3/max_fs = 127
p14a3/max_ss = 255
p14a3/fs = -0.001319x +1.000000y
p14a3/ss = -1.000000x -0.001319y
p14a3/corner_x = 351.248
p14a3/corner_y = 154.863

p14a4/min_fs = 0
p14a4/min_ss = 256
p14a4/max_fs = 127
p14a4/max_ss = 319
p14a4/fs = -0.001319x +1.000000y
p14a4/ss = -1.000000x -0.001319y
p14a4/corner_x = 285.25
p14a4/corner_y = 154.775

p14a5/min_fs = 0
p14a5/min_ss = 320
p14a5/max_fs = 127
p14a5/max_ss = 383
p14a5/fs = -0.001319x +1.000000y
p14a5/ss = -1.000000x -0.001319y
p14a5/corner_x = 219.236
p14a5/corner_y = 154.684

p14a6/min_fs = 0
p14a6/min_ss = 384
p14a6/max_fs = 127
p14a6/max_ss = 447
p14a6/fs = -0.001319x +1.000000y
p14a6/ss = -1.000000x -0.001319y
p14a6/corner_x = 153.235
p14a6/corner_y = 154.594

p14a7/min_fs = 0
p14a7/min_ss = 448
p14a7/max_fs = 127
p14a7/max_ss = 511
p14a7/fs = -0.001319x +1.000000y
p14a7/ss = -1.000000x -0.001319y
p14a7/corner_x = 87.2321
p14a7/corner_y = 154.504

p15a0/min_fs = 0
p15a0/min_ss = 0
p15a0/max_fs = 127
p15a0/max_ss = 63
p15a0/fs = -0.000038x +1.000002y
p15a0/ss = -1.000002x -0.000038y
p15a0/corner_x = 549.286
p15a0/corner_y = -2.04455

p15a1/min_fs = 0
p15a1/min_ss = 64
p15a1/max_fs = 127
p15a1/max_ss = 127
p15a1/fs = -0.000038x +1.000002y
p15a1/ss = -1.000002x -0.000038y
p15a1/corner_x = 483.289
p15a1/corner_y = -2.05336

p15a2/min_fs = 0
p15a2/min_ss = 128
p15a2/max_fs = 127
p15a2/max_ss = 191
p15a2/fs = -0.000038x +1.000002y
p15a2/ss = -1.000002x -0.000038y
p15a2/corner_x = 417.292
p15a2/corner_y = -2.06195

p15a3/min_fs = 0
p15a3/min_ss = 192
p15a3/max_fs = 127
p15a3/max_ss = 255
p15a3/fs = -0.000038x +1.000002y
p15a3/ss = -1.000002x -0.000038y
p15a3/corner_x = 351.294
p15a3/corner_y = -2.07057

p15a4/min_fs = 0
p15a4/min_ss = 256
p15a4/max_fs = 127
p15a4/max_ss = 319
p15a4/fs = -0.000038x +1.000002y
p15a4/ss = -1.000002x -0.000038y
p15a4/corner_x = 285.294
p15a4/corner_y = -2.07915

p15a5/min_fs = 0
p15a5/min_ss = 320
p15a5/max_fs = 127
p15a5/max_ss = 383
p15a5/fs = -0.000038x +1.000002y
p15a5/ss = -1.000002x -0.000038y
p15a5/corner_x = 219.277
p15a5/corner_y = -2.08787

p15a6/min_fs = 0
p15a6/min_ss = 384
p15a6/max_fs = 127
p15a6/max_ss = 447
p15a6/fs = -0.000038x +1.000002y
p15a6/ss = -1.000002x -0.000038y
p15a6/corner_x = 153.276
p15a6/corner_y = -2.09647

p15a7/min_fs = 0
p15a7/min_ss = 448
p15a7/max_fs = 127
p15a7/max_ss = 511
p15a7/fs = -0.000038x +1.000002y
p15a7/ss = -1.000002x -0.000038y
p15a7/corner_x = 87.2746
p15a7/corner_y = -2.10517













p0a0/coffset = 0.000258
p0a1/coffset = 0.000258
p0a2/coffset = 0.000258
p0a3/coffset = 0.000258
p0a4/coffset = 0.000258
p0a5/coffset = 0.000258
p0a6/coffset = 0.000258
p0a7/coffset = 0.000258
p1a0/coffset = 0.000071
p1a1/coffset = 0.000071
p1a2/coffset = 0.000071
p1a3/coffset = 0.000071
p1a4/coffset = 0.000071
p1a5/coffset = 0.000071
p1a6/coffset = 0.000071
p1a7/coffset = 0.000071
p2a0/coffset = 0.000059
p2a1/coffset = 0.000059
p2a2/coffset = 0.000059
p2a3/coffset = 0.000059
p2a4/coffset = 0.000059
p2a5/coffset = 0.000059
p2a6/coffset = 0.000059
p2a7/coffset = 0.000059
p3a0/coffset = 0.000072
p3a1/coffset = 0.000072
p3a2/coffset = 0.000072
p3a3/coffset = 0.000072
p3a4/coffset = 0.000072
p3a5/coffset = 0.000072
p3a6/coffset = 0.000072
p3a7/coffset = 0.000072
p4a0/coffset = 0.000076
p4a1/coffset = 0.000076
p4a2/coffset = 0.000076
p4a3/coffset = 0.000076
p4a4/coffset = 0.000076
p4a5/coffset = 0.000076
p4a6/coffset = 0.000076
p4a7/coffset = 0.000076
p5a0/coffset = 0.000070
p5a1/coffset = 0.000070
p5a2/coffset = 0.000070
p5a3/coffset = 0.000070
p5a4/coffset = 0.000070
p5a5/coffset = 0.000070
p5a6/coffset = 0.000070
p5a7/coffset = 0.000070
p6a0/coffset = 0.000003
p6a1/coffset = 0.000003
p6a2/coffset = 0.000003
p6a3/coffset = 0.000003
p6a4/coffset = 0.000003
p6a5/coffset = 0.000003
p6a6/coffset = 0.000003
p6a7/coffset = 0.000003
p7a0/coffset = 0.000175
p7a1/coffset = 0.000175
p7a2/coffset = 0.000175
p7a3/coffset = 0.000175
p7a4/coffset = 0.000175
p7a5/coffset = 0.000175
p7a6/coffset = 0.000175
p7a7/coffset = 0.000175
p8a0/coffset = -0.000018
p8a1/coffset = -0.000018
p8a2/coffset = -0.000018
p8a3/coffset = -0.000018
p8a4/coffset = -0.000018
p8a5/coffset = -0.000018
p8a6/coffset = -0.000018
p8a7/coffset = -0.000018
p9a0/coffset = 0.000063
p9a1/coffset = 0.000063
p9a2/coffset = 0.000063
p9a3/coffset = 0.000063
p9a4/coffset = 0.000063
p9a5/coffset = 0.000063
p9a6/coffset = 0.000063
p9a7/coffset = 0.000063
p10a0/coffset = -0.000075
p10a1/coffset = -0.000075
p10a2/coffset = -0.000075
p10a3/coffset = -0.000075
p10a4/coffset = -0.000075
p10a5/coffset = -0.000075
p10a6/coffset = -0.000075
p10a7/coffset = -0.000075
p11a0/coffset = -0.000156
p11a1/coffset = -0.000156
p11a2/coffset = -0.000156
p11a3/coffset = -0.000156
p11a4/coffset = -0.000156
p11a5/coffset = -0.000156
p11a6/coffset = -0.000156
p11a7/coffset = -0.000156
p12a0/coffset = -0.000151
p12a1/coffset = -0.000151
p12a2/coffset = -0.000151
p12a3/coffset = -0.000151
p12a4/coffset = -0.000151
p12a5/coffset = -0.000151
p12a6/coffset = -0.000151
p12a7/coffset = -0.000151
p13a0/coffset = -0.000165
p13a1/coffset = -0.000165
p13a2/coffset = -0.000165
p13a3/coffset = -0.000165
p13a4/coffset = -0.000165
p13a5/coffset = -0.000165
p13a6/coffset = -0.000165
p13a7/coffset = -0.000165
p14a0/coffset = -0.000092
p14a1/coffset = -0.000092
p14a2/coffset = -0.000092
p14a3/coffset = -0.000092
p14a4/coffset = -0.000092
p14a5/coffset = -0.000092
p14a6/coffset = -0.000092
p14a7/coffset = -0.000092
p15a0/coffset = -0.000300
p15a1/coffset = -0.000300
p15a2/coffset = -0.000300
p15a3/coffset = -0.000300
p15a4/coffset = -0.000300
p15a5/coffset = -0.000300
p15a6/coffset = -0.000300
p15a7/coffset = -0.000300


p0a0/dim1 = 0
p0a1/dim1 = 0
p0a2/dim1 = 0
p0a3/dim1 = 0
p0a4/dim1 = 0
p0a5/dim1 = 0
p0a6/dim1 = 0
p0a7/dim1 = 0
p1a0/dim1 = 1
p1a1/dim1 = 1
p1a2/dim1 = 1
p1a3/dim1 = 1
p1a4/dim1 = 1
p1a5/dim1 = 1
p1a6/dim1 = 1
p1a7/dim1 = 1
p2a0/dim1 = 2
p2a1/dim1 = 2
p2a2/dim1 = 2
p2a3/dim1 = 2
p2a4/dim1 = 2
p2a5/dim1 = 2
p2a6/dim1 = 2
p2a7/dim1 = 2
p3a0/dim1 = 3
p3a1/dim1 = 3
p3a2/dim1 = 3
p3a3/dim1 = 3
p3a4/dim1 = 3
p3a5/dim1 = 3
p3a6/dim1 = 3
p3a7/dim1 = 3
p4a0/dim1 = 4
p4a1/dim1 = 4
p4a2/dim1 = 4
p4a3/dim1 = 4
p4a4/dim1 = 4
p4a5/dim1 = 4
p4a6/dim1 = 4
p4a7/dim1 = 4
p5a0/dim1 = 5
p5a1/dim1 = 5
p5a2/dim1 = 5
p5a3/dim1 = 5
p5a4/dim1 = 5
p5a5/dim1 = 5
p5a6/dim1 = 5
p5a7/dim1 = 5
p6a0/dim1 = 6
p6a1/dim1 = 6
p6a2/dim1 = 6
p6a3/dim1 = 6
p6a4/dim1 = 6
p6a5/dim1 = 6
p6a6/dim1 = 6
p6a7/dim1 = 6
p7a0/dim1 = 7
p7a1/dim1 = 7
p7a2/dim1 = 7
p7a3/dim1 = 7
p7a4/dim1 = 7
p7a5/dim1 = 7
p7a6/dim1 = 7
p7a7/dim1 = 7
p8a0/dim1 = 8
p8a1/dim1 = 8
p8a2/dim1 = 8
p8a3/dim1 = 8
p8a4/dim1 = 8
p8a5/dim1 = 8
p8a6/dim1 = 8
p8a7/dim1 = 8
p9a0/dim1 = 9
p9a1/dim1 = 9
p9a2/dim1 = 9
p9a3/dim1 = 9
p9a4/dim1 = 9
p9a5/dim1 = 9
p9a6/dim1 = 9
p9a7/dim1 = 9
p10a0/dim1 = 10
p10a1/dim1 = 10
p10a2/dim1 = 10
p10a3/dim1 = 10
p10a4/dim1 = 10
p10a5/dim1 = 10
p10a6/dim1 = 10
p10a7/dim1 = 10
p11a0/dim1 = 11
p11a1/dim1 = 11
p11a2/dim1 = 11
p11a3/dim1 = 11
p11a4/dim1 = 11
p11a5/dim1 = 11
p11a6/dim1 = 11
p11a7/dim1 = 11
p12a0/dim1 = 12
p12a1/dim1 = 12
p12a2/dim1 = 12
p12a3/dim1 = 12
p12a4/dim1 = 12
p12a5/dim1 = 12
p12a6/dim1 = 12
p12a7/dim1 = 12
p13a0/dim1 = 13
p13a1/dim1 = 13
p13a2/dim1 = 13
p13a3/dim1 = 13
p13a4/dim1 = 13
p13a5/dim1 = 13
p13a6/dim1 = 13
p13a7/dim1 = 13
p14a0/dim1 = 14
p14a1/dim1 = 14
p14a2/dim1 = 14
p14a3/dim1 = 14
p14a4/dim1 = 14
p14a5/dim1 = 14
p14a6/dim1 = 14
p14a7/dim1 = 14
p15a0/dim1 = 15
p15a1/dim1 = 15
p15a2/dim1 = 15
p15a3/dim1 = 15
p15a4/dim1 = 15
p15a5/dim1 = 15
p15a6/dim1 = 15
p15a7/dim1 = 15


p0a0/dim2 = ss
p0a1/dim2 = ss
p0a2/dim2 = ss
p0a3/dim2 = ss
p0a4/dim2 = ss
p0a5/dim2 = ss
p0a6/dim2 = ss
p0a7/dim2 = ss
p1a0/dim2 = ss
p1a1/dim2 = ss
p1a2/dim2 = ss
p1a3/dim2 = ss
p1a4/dim2 = ss
p1a5/dim2 = ss
p1a6/dim2 = ss
p1a7/dim2 = ss
p2a0/dim2 = ss
p2a1/dim2 = ss
p2a2/dim2 = ss
p2a3/dim2 = ss
p2a4/dim2 = ss
p2a5/dim2 = ss
p2a6/dim2 = ss
p2a7/dim2 = ss
p3a0/dim2 = ss
p3a1/dim2 = ss
p3a2/dim2 = ss
p3a3/dim2 = ss
p3a4/dim2 = ss
p3a5/dim2 = ss
p3a6/dim2 = ss
p3a7/dim2 = ss
p4a0/dim2 = ss
p4a1/dim2 = ss
p4a2/dim2 = ss
p4a3/dim2 = ss
p4a4/dim2 = ss
p4a5/dim2 = ss
p4a6/dim2 = ss
p4a7/dim2 = ss
p5a0/dim2 = ss
p5a1/dim2 = ss
p5a2/dim2 = ss
p5a3/dim2 = ss
p5a4/dim2 = ss
p5a5/dim2 = ss
p5a6/dim2 = ss
p5a7/dim2 = ss
p6a0/dim2 = ss
p6a1/dim2 = ss
p6a2/dim2 = ss
p6a3/dim2 = ss
p6a4/dim2 = ss
p6a5/dim2 = ss
p6a6/dim2 = ss
p6a7/dim2 = ss
p7a0/dim2 = ss
p7a1/dim2 = ss
p7a2/dim2 = ss
p7a3/dim2 = ss
p7a4/dim2 = ss
p7a5/dim2 = ss
p7a6/dim2 = ss
p7a7/dim2 = ss
p8a0/dim2 = ss
p8a1/dim2 = ss
p8a2/dim2 = ss
p8a3/dim2 = ss
p8a4/dim2 = ss
p8a5/dim2 = ss
p8a6/dim2 = ss
p8a7/dim2 = ss
p9a0/dim2 = ss
p9a1/dim2 = ss
p9a2/dim2 = ss
p9a3/dim2 = ss
p9a4/dim2 = ss
p9a5/dim2 = ss
p9a6/dim2 = ss
p9a7/dim2 = ss
p10a0/dim2 = ss
p10a1/dim2 = ss
p10a2/dim2 = ss
p10a3/dim2 = ss
p10a4/dim2 = ss
p10a5/dim2 = ss
p10a6/dim2 = ss
p10a7/dim2 = ss
p11a0/dim2 = ss
p11a1/dim2 = ss
p11a2/dim2 = ss
p11a3/dim2 = ss
p11a4/dim2 = ss
p11a5/dim2 = ss
p11a6/dim2 = ss
p11a7/dim2 = ss
p12a0/dim2 = ss
p12a1/dim2 = ss
p12a2/dim2 = ss
p12a3/dim2 = ss
p12a4/dim2 = ss
p12a5/dim2 = ss
p12a6/dim2 = ss
p12a7/dim2 = ss
p13a0/dim2 = ss
p13a1/dim2 = ss
p13a2/dim2 = ss
p13a3/dim2 = ss
p13a4/dim2 = ss
p13a5/dim2 = ss
p13a6/dim2 = ss
p13a7/dim2 = ss
p14a0/dim2 = ss
p14a1/dim2 = ss
p14a2/dim2 = ss
p14a3/dim2 = ss
p14a4/dim2 = ss
p14a5/dim2 = ss
p14a6/dim2 = ss
p14a7/dim2 = ss
p15a0/dim2 = ss
p15a1/dim2 = ss
p15a2/dim2 = ss
p15a3/dim2 = ss
p15a4/dim2 = ss
p15a5/dim2 = ss
p15a6/dim2 = ss
p15a7/dim2 = ss


p0a0/dim3 = fs
p0a1/dim3 = fs
p0a2/dim3 = fs
p0a3/dim3 = fs
p0a4/dim3 = fs
p0a5/dim3 = fs
p0a6/dim3 = fs
p0a7/dim3 = fs
p1a0/dim3 = fs
p1a1/dim3 = fs
p1a2/dim3 = fs
p1a3/dim3 = fs
p1a4/dim3 = fs
p1a5/dim3 = fs
p1a6/dim3 = fs
p1a7/dim3 = fs
p2a0/dim3 = fs
p2a1/dim3 = fs
p2a2/dim3 = fs
p2a3/dim3 = fs
p2a4/dim3 = fs
p2a5/dim3 = fs
p2a6/dim3 = fs
p2a7/dim3 = fs
p3a0/dim3 = fs
p3a1/dim3 = fs
p3a2/dim3 = fs
p3a3/dim3 = fs
p3a4/dim3 = fs
p3a5/dim3 = fs
p3a6/dim3 = fs
p3a7/dim3 = fs
p4a0/dim3 = fs
p4a1/dim3 = fs
p4a2/dim3 = fs
p4a3/dim3 = fs
p4a4/dim3 = fs
p4a5/dim3 = fs
p4a6/dim3 = fs
p4a7/dim3 = fs
p5a0/dim3 = fs
p5a1/dim3 = fs
p5a2/dim3 = fs
p5a3/dim3 = fs
p5a4/dim3 = fs
p5a5/dim3 = fs
p5a6/dim3 = fs
p5a7/dim3 = fs
p6a0/dim3 = fs
p6a1/dim3 = fs
p6a2/dim3 = fs
p6a3/dim3 = fs
p6a4/dim3 = fs
p6a5/dim3 = fs
p6a6/dim3 = fs
p6a7/dim3 = fs
p7a0/dim3 = fs
p7a1/dim3 = fs
p7a2/dim3 = fs
p7a3/dim3 = fs
p7a4/dim3 = fs
p7a5/dim3 = fs
p7a6/dim3 = fs
p7a7/dim3 = fs
p8a0/dim3 = fs
p8a1/dim3 = fs
p8a2/dim3 = fs
p8a3/dim3 = fs
p8a4/dim3 = fs
p8a5/dim3 = fs
p8a6/dim3 = fs
p8a7/dim3 = fs
p9a0/dim3 = fs
p9a1/dim3 = fs
p9a2/dim3 = fs
p9a3/dim3 = fs
p9a4/dim3 = fs
p9a5/dim3 = fs
p9a6/dim3 = fs
p9a7/dim3 = fs
p10a0/dim3 = fs
p10a1/dim3 = fs
p10a2/dim3 = fs
p10a3/dim3 = fs
p10a4/dim3 = fs
p10a5/dim3 = fs
p10a6/dim3 = fs
p10a7/dim3 = fs
p11a0/dim3 = fs
p11a1/dim3 = fs
p11a2/dim3 = fs
p11a3/dim3 = fs
p11a4/dim3 = fs
p11a5/dim3 = fs
p11a6/dim3 = fs
p11a7/dim3 = fs
p12a0/dim3 = fs
p12a1/dim3 = fs
p12a2/dim3 = fs
p12a3/dim3 = fs
p12a4/dim3 = fs
p12a5/dim3 = fs
p12a6/dim3 = fs
p12a7/dim3 = fs
p13a0/dim3 = fs
p13a1/dim3 = fs
p13a2/dim3 = fs
p13a3/dim3 = fs
p13a4/dim3 = fs
p13a5/dim3 = fs
p13a6/dim3 = fs
p13a7/dim3 = fs
p14a0/dim3 = fs
p14a1/dim3 = fs
p14a2/dim3 = fs
p14a3/dim3 = fs
p14a4/dim3 = fs
p14a5/dim3 = fs
p14a6/dim3 = fs
p14a7/dim3 = fs
p15a0/dim3 = fs
p15a1/dim3 = fs
p15a2/dim3 = fs
p15a3/dim3 = fs
p15a4/dim3 = fs
p15a5/dim3 = fs
p15a6/dim3 = fs
p15a7/dim3 = fs

bad_p0h1/min_ss = 0
bad_p0h1/min_fs = 0
bad_p0h1/max_ss = 511
bad_p0h1/max_fs = 4
bad_p0h1/dim1 = 0
bad_p0h1/dim2 = ss
bad_p0h1/dim3 = fs

bad_p0h2/min_ss = 0
bad_p0h2/min_fs = 123
bad_p0h2/max_ss = 511
bad_p0h2/max_fs = 127
bad_p0h2/dim1 = 0
bad_p0h2/dim2 = ss
bad_p0h2/dim3 = fs

bad_p0v1/min_ss = 0
bad_p0v1/min_fs = 0
bad_p0v1/max_ss = 4
bad_p0v1/max_fs = 127
bad_p0v1/dim1 = 0
bad_p0v1/dim2 = ss
bad_p0v1/dim3 = fs

bad_p0v2/min_ss = 59
bad_p0v2/min_fs = 0
bad_p0v2/max_ss = 68
bad_p0v2/max_fs = 127
bad_p0v2/dim1 = 0
bad_p0v2/dim2 = ss
bad_p0v2/dim3 = fs

bad_p0v3/min_ss = 123
bad_p0v3/min_fs = 0
bad_p0v3/max_ss = 132
bad_p0v3/max_fs = 127
bad_p0v3/dim1 = 0
bad_p0v3/dim2 = ss
bad_p0v3/dim3 = fs

bad_p0v4/min_ss = 187
bad_p0v4/min_fs = 0
bad_p0v4/max_ss = 196
bad_p0v4/max_fs = 127
bad_p0v4/dim1 = 0
bad_p0v4/dim2 = ss
bad_p0v4/dim3 = fs

bad_p0v5/min_ss = 251
bad_p0v5/min_fs = 0
bad_p0v5/max_ss = 260
bad_p0v5/max_fs = 127
bad_p0v5/dim1 = 0
bad_p0v5/dim2 = ss
bad_p0v5/dim3 = fs

bad_p0v6/min_ss = 315
bad_p0v6/min_fs = 0
bad_p0v6/max_ss = 324
bad_p0v6/max_fs = 127
bad_p0v6/dim1 = 0
bad_p0v6/dim2 = ss
bad_p0v6/dim3 = fs

bad_p0v7/min_ss = 379
bad_p0v7/min_fs = 0
bad_p0v7/max_ss = 388
bad_p0v7/max_fs = 127
bad_p0v7/dim1 = 0
bad_p0v7/dim2 = ss
bad_p0v7/dim3 = fs

bad_p0v8/min_ss = 443
bad_p0v8/min_fs = 0
bad_p0v8/max_ss = 452
bad_p0v8/max_fs = 127
bad_p0v8/dim1 = 0
bad_p0v8/dim2 = ss
bad_p0v8/dim3 = fs

bad_p0v9/min_ss = 507
bad_p0v9/min_fs = 0
bad_p0v9/max_ss = 511
bad_p0v9/max_fs = 127
bad_p0v9/dim1 = 0
bad_p0v9/dim2 = ss
bad_p0v9/dim3 = fs
bad_p1h1/min_ss = 0
bad_p1h1/min_fs = 0
bad_p1h1/max_ss = 511
bad_p1h1/max_fs = 4
bad_p1h1/dim1 = 1
bad_p1h1/dim2 = ss
bad_p1h1/dim3 = fs

bad_p1h2/min_ss = 0
bad_p1h2/min_fs = 123
bad_p1h2/max_ss = 511
bad_p1h2/max_fs = 127
bad_p1h2/dim1 = 1
bad_p1h2/dim2 = ss
bad_p1h2/dim3 = fs

bad_p1v1/min_ss = 0
bad_p1v1/min_fs = 0
bad_p1v1/max_ss = 4
bad_p1v1/max_fs = 127
bad_p1v1/dim1 = 1
bad_p1v1/dim2 = ss
bad_p1v1/dim3 = fs

bad_p1v2/min_ss = 59
bad_p1v2/min_fs = 0
bad_p1v2/max_ss = 68
bad_p1v2/max_fs = 127
bad_p1v2/dim1 = 1
bad_p1v2/dim2 = ss
bad_p1v2/dim3 = fs

bad_p1v3/min_ss = 123
bad_p1v3/min_fs = 0
bad_p1v3/max_ss = 132
bad_p1v3/max_fs = 127
bad_p1v3/dim1 = 1
bad_p1v3/dim2 = ss
bad_p1v3/dim3 = fs

bad_p1v4/min_ss = 187
bad_p1v4/min_fs = 0
bad_p1v4/max_ss = 196
bad_p1v4/max_fs = 127
bad_p1v4/dim1 = 1
bad_p1v4/dim2 = ss
bad_p1v4/dim3 = fs

bad_p1v5/min_ss = 251
bad_p1v5/min_fs = 0
bad_p1v5/max_ss = 260
bad_p1v5/max_fs = 127
bad_p1v5/dim1 = 1
bad_p1v5/dim2 = ss
bad_p1v5/dim3 = fs

bad_p1v6/min_ss = 315
bad_p1v6/min_fs = 0
bad_p1v6/max_ss = 324
bad_p1v6/max_fs = 127
bad_p1v6/dim1 = 1
bad_p1v6/dim2 = ss
bad_p1v6/dim3 = fs

bad_p1v7/min_ss = 379
bad_p1v7/min_fs = 0
bad_p1v7/max_ss = 388
bad_p1v7/max_fs = 127
bad_p1v7/dim1 = 1
bad_p1v7/dim2 = ss
bad_p1v7/dim3 = fs

bad_p1v8/min_ss = 443
bad_p1v8/min_fs = 0
bad_p1v8/max_ss = 452
bad_p1v8/max_fs = 127
bad_p1v8/dim1 = 1
bad_p1v8/dim2 = ss
bad_p1v8/dim3 = fs

bad_p1v9/min_ss = 507
bad_p1v9/min_fs = 0
bad_p1v9/max_ss = 511
bad_p1v9/max_fs = 127
bad_p1v9/dim1 = 1
bad_p1v9/dim2 = ss
bad_p1v9/dim3 = fs
bad_p2h1/min_ss = 0
bad_p2h1/min_fs = 0
bad_p2h1/max_ss = 511
bad_p2h1/max_fs = 4
bad_p2h1/dim1 = 2
bad_p2h1/dim2 = ss
bad_p2h1/dim3 = fs

bad_p2h2/min_ss = 0
bad_p2h2/min_fs = 123
bad_p2h2/max_ss = 511
bad_p2h2/max_fs = 127
bad_p2h2/dim1 = 2
bad_p2h2/dim2 = ss
bad_p2h2/dim3 = fs

bad_p2v1/min_ss = 0
bad_p2v1/min_fs = 0
bad_p2v1/max_ss = 4
bad_p2v1/max_fs = 127
bad_p2v1/dim1 = 2
bad_p2v1/dim2 = ss
bad_p2v1/dim3 = fs

bad_p2v2/min_ss = 59
bad_p2v2/min_fs = 0
bad_p2v2/max_ss = 68
bad_p2v2/max_fs = 127
bad_p2v2/dim1 = 2
bad_p2v2/dim2 = ss
bad_p2v2/dim3 = fs

bad_p2v3/min_ss = 123
bad_p2v3/min_fs = 0
bad_p2v3/max_ss = 132
bad_p2v3/max_fs = 127
bad_p2v3/dim1 = 2
bad_p2v3/dim2 = ss
bad_p2v3/dim3 = fs

bad_p2v4/min_ss = 187
bad_p2v4/min_fs = 0
bad_p2v4/max_ss = 196
bad_p2v4/max_fs = 127
bad_p2v4/dim1 = 2
bad_p2v4/dim2 = ss
bad_p2v4/dim3 = fs

bad_p2v5/min_ss = 251
bad_p2v5/min_fs = 0
bad_p2v5/max_ss = 260
bad_p2v5/max_fs = 127
bad_p2v5/dim1 = 2
bad_p2v5/dim2 = ss
bad_p2v5/dim3 = fs

bad_p2v6/min_ss = 315
bad_p2v6/min_fs = 0
bad_p2v6/max_ss = 324
bad_p2v6/max_fs = 127
bad_p2v6/dim1 = 2
bad_p2v6/dim2 = ss
bad_p2v6/dim3 = fs

bad_p2v7/min_ss = 379
bad_p2v7/min_fs = 0
bad_p2v7/max_ss = 388
bad_p2v7/max_fs = 127
bad_p2v7/dim1 = 2
bad_p2v7/dim2 = ss
bad_p2v7/dim3 = fs

bad_p2v8/min_ss = 443
bad_p2v8/min_fs = 0
bad_p2v8/max_ss = 452
bad_p2v8/max_fs = 127
bad_p2v8/dim1 = 2
bad_p2v8/dim2 = ss
bad_p2v8/dim3 = fs

bad_p2v9/min_ss = 507
bad_p2v9/min_fs = 0
bad_p2v9/max_ss = 511
bad_p2v9/max_fs = 127
bad_p2v9/dim1 = 2
bad_p2v9/dim2 = ss
bad_p2v9/dim3 = fs
bad_p3h1/min_ss = 0
bad_p3h1/min_fs = 0
bad_p3h1/max_ss = 511
bad_p3h1/max_fs = 4
bad_p3h1/dim1 = 3
bad_p3h1/dim2 = ss
bad_p3h1/dim3 = fs

bad_p3h2/min_ss = 0
bad_p3h2/min_fs = 123
bad_p3h2/max_ss = 511
bad_p3h2/max_fs = 127
bad_p3h2/dim1 = 3
bad_p3h2/dim2 = ss
bad_p3h2/dim3 = fs

bad_p3v1/min_ss = 0
bad_p3v1/min_fs = 0
bad_p3v1/max_ss = 4
bad_p3v1/max_fs = 127
bad_p3v1/dim1 = 3
bad_p3v1/dim2 = ss
bad_p3v1/dim3 = fs

bad_p3v2/min_ss = 59
bad_p3v2/min_fs = 0
bad_p3v2/max_ss = 68
bad_p3v2/max_fs = 127
bad_p3v2/dim1 = 3
bad_p3v2/dim2 = ss
bad_p3v2/dim3 = fs

bad_p3v3/min_ss = 123
bad_p3v3/min_fs = 0
bad_p3v3/max_ss = 132
bad_p3v3/max_fs = 127
bad_p3v3/dim1 = 3
bad_p3v3/dim2 = ss
bad_p3v3/dim3 = fs

bad_p3v4/min_ss = 187
bad_p3v4/min_fs = 0
bad_p3v4/max_ss = 196
bad_p3v4/max_fs = 127
bad_p3v4/dim1 = 3
bad_p3v4/dim2 = ss
bad_p3v4/dim3 = fs

bad_p3v5/min_ss = 251
bad_p3v5/min_fs = 0
bad_p3v5/max_ss = 260
bad_p3v5/max_fs = 127
bad_p3v5/dim1 = 3
bad_p3v5/dim2 = ss
bad_p3v5/dim3 = fs

bad_p3v6/min_ss = 315
bad_p3v6/min_fs = 0
bad_p3v6/max_ss = 324
bad_p3v6/max_fs = 127
bad_p3v6/dim1 = 3
bad_p3v6/dim2 = ss
bad_p3v6/dim3 = fs

bad_p3v7/min_ss = 379
bad_p3v7/min_fs = 0
bad_p3v7/max_ss = 388
bad_p3v7/max_fs = 127
bad_p3v7/dim1 = 3
bad_p3v7/dim2 = ss
bad_p3v7/dim3 = fs

bad_p3v8/min_ss = 443
bad_p3v8/min_fs = 0
bad_p3v8/max_ss = 452
bad_p3v8/max_fs = 127
bad_p3v8/dim1 = 3
bad_p3v8/dim2 = ss
bad_p3v8/dim3 = fs

bad_p3v9/min_ss = 507
bad_p3v9/min_fs = 0
bad_p3v9/max_ss = 511
bad_p3v9/max_fs = 127
bad_p3v9/dim1 = 3
bad_p3v9/dim2 = ss
bad_p3v9/dim3 = fs
bad_p4h1/min_ss = 0
bad_p4h1/min_fs = 0
bad_p4h1/max_ss = 511
bad_p4h1/max_fs = 4
bad_p4h1/dim1 = 4
bad_p4h1/dim2 = ss
bad_p4h1/dim3 = fs

bad_p4h2/min_ss = 0
bad_p4h2/min_fs = 123
bad_p4h2/max_ss = 511
bad_p4h2/max_fs = 127
bad_p4h2/dim1 = 4
bad_p4h2/dim2 = ss
bad_p4h2/dim3 = fs

bad_p4v1/min_ss = 0
bad_p4v1/min_fs = 0
bad_p4v1/max_ss = 4
bad_p4v1/max_fs = 127
bad_p4v1/dim1 = 4
bad_p4v1/dim2 = ss
bad_p4v1/dim3 = fs

bad_p4v2/min_ss = 59
bad_p4v2/min_fs = 0
bad_p4v2/max_ss = 68
bad_p4v2/max_fs = 127
bad_p4v2/dim1 = 4
bad_p4v2/dim2 = ss
bad_p4v2/dim3 = fs

bad_p4v3/min_ss = 123
bad_p4v3/min_fs = 0
bad_p4v3/max_ss = 132
bad_p4v3/max_fs = 127
bad_p4v3/dim1 = 4
bad_p4v3/dim2 = ss
bad_p4v3/dim3 = fs

bad_p4v4/min_ss = 187
bad_p4v4/min_fs = 0
bad_p4v4/max_ss = 196
bad_p4v4/max_fs = 127
bad_p4v4/dim1 = 4
bad_p4v4/dim2 = ss
bad_p4v4/dim3 = fs

bad_p4v5/min_ss = 251
bad_p4v5/min_fs = 0
bad_p4v5/max_ss = 260
bad_p4v5/max_fs = 127
bad_p4v5/dim1 = 4
bad_p4v5/dim2 = ss
bad_p4v5/dim3 = fs

bad_p4v6/min_ss = 315
bad_p4v6/min_fs = 0
bad_p4v6/max_ss = 324
bad_p4v6/max_fs = 127
bad_p4v6/dim1 = 4
bad_p4v6/dim2 = ss
bad_p4v6/dim3 = fs

bad_p4v7/min_ss = 379
bad_p4v7/min_fs = 0
bad_p4v7/max_ss = 388
bad_p4v7/max_fs = 127
bad_p4v7/dim1 = 4
bad_p4v7/dim2 = ss
bad_p4v7/dim3 = fs

bad_p4v8/min_ss = 443
bad_p4v8/min_fs = 0
bad_p4v8/max_ss = 452
bad_p4v8/max_fs = 127
bad_p4v8/dim1 = 4
bad_p4v8/dim2 = ss
bad_p4v8/dim3 = fs

bad_p4v9/min_ss = 507
bad_p4v9/min_fs = 0
bad_p4v9/max_ss = 511
bad_p4v9/max_fs = 127
bad_p4v9/dim1 = 4
bad_p4v9/dim2 = ss
bad_p4v9/dim3 = fs
bad_p5h1/min_ss = 0
bad_p5h1/min_fs = 0
bad_p5h1/max_ss = 511
bad_p5h1/max_fs = 4
bad_p5h1/dim1 = 5
bad_p5h1/dim2 = ss
bad_p5h1/dim3 = fs

bad_p5h2/min_ss = 0
bad_p5h2/min_fs = 123
bad_p5h2/max_ss = 511
bad_p5h2/max_fs = 127
bad_p5h2/dim1 = 5
bad_p5h2/dim2 = ss
bad_p5h2/dim3 = fs

bad_p5v1/min_ss = 0
bad_p5v1/min_fs = 0
bad_p5v1/max_ss = 4
bad_p5v1/max_fs = 127
bad_p5v1/dim1 = 5
bad_p5v1/dim2 = ss
bad_p5v1/dim3 = fs

bad_p5v2/min_ss = 59
bad_p5v2/min_fs = 0
bad_p5v2/max_ss = 68
bad_p5v2/max_fs = 127
bad_p5v2/dim1 = 5
bad_p5v2/dim2 = ss
bad_p5v2/dim3 = fs

bad_p5v3/min_ss = 123
bad_p5v3/min_fs = 0
bad_p5v3/max_ss = 132
bad_p5v3/max_fs = 127
bad_p5v3/dim1 = 5
bad_p5v3/dim2 = ss
bad_p5v3/dim3 = fs

bad_p5v4/min_ss = 187
bad_p5v4/min_fs = 0
bad_p5v4/max_ss = 196
bad_p5v4/max_fs = 127
bad_p5v4/dim1 = 5
bad_p5v4/dim2 = ss
bad_p5v4/dim3 = fs

bad_p5v5/min_ss = 251
bad_p5v5/min_fs = 0
bad_p5v5/max_ss = 260
bad_p5v5/max_fs = 127
bad_p5v5/dim1 = 5
bad_p5v5/dim2 = ss
bad_p5v5/dim3 = fs

bad_p5v6/min_ss = 315
bad_p5v6/min_fs = 0
bad_p5v6/max_ss = 324
bad_p5v6/max_fs = 127
bad_p5v6/dim1 = 5
bad_p5v6/dim2 = ss
bad_p5v6/dim3 = fs

bad_p5v7/min_ss = 379
bad_p5v7/min_fs = 0
bad_p5v7/max_ss = 388
bad_p5v7/max_fs = 127
bad_p5v7/dim1 = 5
bad_p5v7/dim2 = ss
bad_p5v7/dim3 = fs

bad_p5v8/min_ss = 443
bad_p5v8/min_fs = 0
bad_p5v8/max_ss = 452
bad_p5v8/max_fs = 127
bad_p5v8/dim1 = 5
bad_p5v8/dim2 = ss
bad_p5v8/dim3 = fs

bad_p5v9/min_ss = 507
bad_p5v9/min_fs = 0
bad_p5v9/max_ss = 511
bad_p5v9/max_fs = 127
bad_p5v9/dim1 = 5
bad_p5v9/dim2 = ss
bad_p5v9/dim3 = fs
bad_p6h1/min_ss = 0
bad_p6h1/min_fs = 0
bad_p6h1/max_ss = 511
bad_p6h1/max_fs = 4
bad_p6h1/dim1 = 6
bad_p6h1/dim2 = ss
bad_p6h1/dim3 = fs

bad_p6h2/min_ss = 0
bad_p6h2/min_fs = 123
bad_p6h2/max_ss = 511
bad_p6h2/max_fs = 127
bad_p6h2/dim1 = 6
bad_p6h2/dim2 = ss
bad_p6h2/dim3 = fs

bad_p6v1/min_ss = 0
bad_p6v1/min_fs = 0
bad_p6v1/max_ss = 4
bad_p6v1/max_fs = 127
bad_p6v1/dim1 = 6
bad_p6v1/dim2 = ss
bad_p6v1/dim3 = fs

bad_p6v2/min_ss = 59
bad_p6v2/min_fs = 0
bad_p6v2/max_ss = 68
bad_p6v2/max_fs = 127
bad_p6v2/dim1 = 6
bad_p6v2/dim2 = ss
bad_p6v2/dim3 = fs

bad_p6v3/min_ss = 123
bad_p6v3/min_fs = 0
bad_p6v3/max_ss = 132
bad_p6v3/max_fs = 127
bad_p6v3/dim1 = 6
bad_p6v3/dim2 = ss
bad_p6v3/dim3 = fs

bad_p6v4/min_ss = 187
bad_p6v4/min_fs = 0
bad_p6v4/max_ss = 196
bad_p6v4/max_fs = 127
bad_p6v4/dim1 = 6
bad_p6v4/dim2 = ss
bad_p6v4/dim3 = fs

bad_p6v5/min_ss = 251
bad_p6v5/min_fs = 0
bad_p6v5/max_ss = 260
bad_p6v5/max_fs = 127
bad_p6v5/dim1 = 6
bad_p6v5/dim2 = ss
bad_p6v5/dim3 = fs

bad_p6v6/min_ss = 315
bad_p6v6/min_fs = 0
bad_p6v6/max_ss = 324
bad_p6v6/max_fs = 127
bad_p6v6/dim1 = 6
bad_p6v6/dim2 = ss
bad_p6v6/dim3 = fs

bad_p6v7/min_ss = 379
bad_p6v7/min_fs = 0
bad_p6v7/max_ss = 388
bad_p6v7/max_fs = 127
bad_p6v7/dim1 = 6
bad_p6v7/dim2 = ss
bad_p6v7/dim3 = fs

bad_p6v8/min_ss = 443
bad_p6v8/min_fs = 0
bad_p6v8/max_ss = 452
bad_p6v8/max_fs = 127
bad_p6v8/dim1 = 6
bad_p6v8/dim2 = ss
bad_p6v8/dim3 = fs

bad_p6v9/min_ss = 507
bad_p6v9/min_fs = 0
bad_p6v9/max_ss = 511
bad_p6v9/max_fs = 127
bad_p6v9/dim1 = 6
bad_p6v9/dim2 = ss
bad_p6v9/dim3 = fs
bad_p7h1/min_ss = 0
bad_p7h1/min_fs = 0
bad_p7h1/max_ss = 511
bad_p7h1/max_fs = 4
bad_p7h1/dim1 = 7
bad_p7h1/dim2 = ss
bad_p7h1/dim3 = fs

bad_p7h2/min_ss = 0
bad_p7h2/min_fs = 123
bad_p7h2/max_ss = 511
bad_p7h2/max_fs = 127
bad_p7h2/dim1 = 7
bad_p7h2/dim2 = ss
bad_p7h2/dim3 = fs

bad_p7v1/min_ss = 0
bad_p7v1/min_fs = 0
bad_p7v1/max_ss = 4
bad_p7v1/max_fs = 127
bad_p7v1/dim1 = 7
bad_p7v1/dim2 = ss
bad_p7v1/dim3 = fs

bad_p7v2/min_ss = 59
bad_p7v2/min_fs = 0
bad_p7v2/max_ss = 68
bad_p7v2/max_fs = 127
bad_p7v2/dim1 = 7
bad_p7v2/dim2 = ss
bad_p7v2/dim3 = fs

bad_p7v3/min_ss = 123
bad_p7v3/min_fs = 0
bad_p7v3/max_ss = 132
bad_p7v3/max_fs = 127
bad_p7v3/dim1 = 7
bad_p7v3/dim2 = ss
bad_p7v3/dim3 = fs

bad_p7v4/min_ss = 187
bad_p7v4/min_fs = 0
bad_p7v4/max_ss = 196
bad_p7v4/max_fs = 127
bad_p7v4/dim1 = 7
bad_p7v4/dim2 = ss
bad_p7v4/dim3 = fs

bad_p7v5/min_ss = 251
bad_p7v5/min_fs = 0
bad_p7v5/max_ss = 260
bad_p7v5/max_fs = 127
bad_p7v5/dim1 = 7
bad_p7v5/dim2 = ss
bad_p7v5/dim3 = fs

bad_p7v6/min_ss = 315
bad_p7v6/min_fs = 0
bad_p7v6/max_ss = 324
bad_p7v6/max_fs = 127
bad_p7v6/dim1 = 7
bad_p7v6/dim2 = ss
bad_p7v6/dim3 = fs

bad_p7v7/min_ss = 379
bad_p7v7/min_fs = 0
bad_p7v7/max_ss = 388
bad_p7v7/max_fs = 127
bad_p7v7/dim1 = 7
bad_p7v7/dim2 = ss
bad_p7v7/dim3 = fs

bad_p7v8/min_ss = 443
bad_p7v8/min_fs = 0
bad_p7v8/max_ss = 452
bad_p7v8/max_fs = 127
bad_p7v8/dim1 = 7
bad_p7v8/dim2 = ss
bad_p7v8/dim3 = fs

bad_p7v9/min_ss = 507
bad_p7v9/min_fs = 0
bad_p7v9/max_ss = 511
bad_p7v9/max_fs = 127
bad_p7v9/dim1 = 7
bad_p7v9/dim2 = ss
bad_p7v9/dim3 = fs
bad_p8h1/min_ss = 0
bad_p8h1/min_fs = 0
bad_p8h1/max_ss = 511
bad_p8h1/max_fs = 4
bad_p8h1/dim1 = 8
bad_p8h1/dim2 = ss
bad_p8h1/dim3 = fs

bad_p8h2/min_ss = 0
bad_p8h2/min_fs = 123
bad_p8h2/max_ss = 511
bad_p8h2/max_fs = 127
bad_p8h2/dim1 = 8
bad_p8h2/dim2 = ss
bad_p8h2/dim3 = fs

bad_p8v1/min_ss = 0
bad_p8v1/min_fs = 0
bad_p8v1/max_ss = 4
bad_p8v1/max_fs = 127
bad_p8v1/dim1 = 8
bad_p8v1/dim2 = ss
bad_p8v1/dim3 = fs

bad_p8v2/min_ss = 59
bad_p8v2/min_fs = 0
bad_p8v2/max_ss = 68
bad_p8v2/max_fs = 127
bad_p8v2/dim1 = 8
bad_p8v2/dim2 = ss
bad_p8v2/dim3 = fs

bad_p8v3/min_ss = 123
bad_p8v3/min_fs = 0
bad_p8v3/max_ss = 132
bad_p8v3/max_fs = 127
bad_p8v3/dim1 = 8
bad_p8v3/dim2 = ss
bad_p8v3/dim3 = fs

bad_p8v4/min_ss = 187
bad_p8v4/min_fs = 0
bad_p8v4/max_ss = 196
bad_p8v4/max_fs = 127
bad_p8v4/dim1 = 8
bad_p8v4/dim2 = ss
bad_p8v4/dim3 = fs

bad_p8v5/min_ss = 251
bad_p8v5/min_fs = 0
bad_p8v5/max_ss = 260
bad_p8v5/max_fs = 127
bad_p8v5/dim1 = 8
bad_p8v5/dim2 = ss
bad_p8v5/dim3 = fs

bad_p8v6/min_ss = 315
bad_p8v6/min_fs = 0
bad_p8v6/max_ss = 324
bad_p8v6/max_fs = 127
bad_p8v6/dim1 = 8
bad_p8v6/dim2 = ss
bad_p8v6/dim3 = fs

bad_p8v7/min_ss = 379
bad_p8v7/min_fs = 0
bad_p8v7/max_ss = 388
bad_p8v7/max_fs = 127
bad_p8v7/dim1 = 8
bad_p8v7/dim2 = ss
bad_p8v7/dim3 = fs

bad_p8v8/min_ss = 443
bad_p8v8/min_fs = 0
bad_p8v8/max_ss = 452
bad_p8v8/max_fs = 127
bad_p8v8/dim1 = 8
bad_p8v8/dim2 = ss
bad_p8v8/dim3 = fs

bad_p8v9/min_ss = 507
bad_p8v9/min_fs = 0
bad_p8v9/max_ss = 511
bad_p8v9/max_fs = 127
bad_p8v9/dim1 = 8
bad_p8v9/dim2 = ss
bad_p8v9/dim3 = fs
bad_p9h1/min_ss = 0
bad_p9h1/min_fs = 0
bad_p9h1/max_ss = 511
bad_p9h1/max_fs = 4
bad_p9h1/dim1 = 9
bad_p9h1/dim2 = ss
bad_p9h1/dim3 = fs

bad_p9h2/min_ss = 0
bad_p9h2/min_fs = 123
bad_p9h2/max_ss = 511
bad_p9h2/max_fs = 127
bad_p9h2/dim1 = 9
bad_p9h2/dim2 = ss
bad_p9h2/dim3 = fs

bad_p9v1/min_ss = 0
bad_p9v1/min_fs = 0
bad_p9v1/max_ss = 4
bad_p9v1/max_fs = 127
bad_p9v1/dim1 = 9
bad_p9v1/dim2 = ss
bad_p9v1/dim3 = fs

bad_p9v2/min_ss = 59
bad_p9v2/min_fs = 0
bad_p9v2/max_ss = 68
bad_p9v2/max_fs = 127
bad_p9v2/dim1 = 9
bad_p9v2/dim2 = ss
bad_p9v2/dim3 = fs

bad_p9v3/min_ss = 123
bad_p9v3/min_fs = 0
bad_p9v3/max_ss = 132
bad_p9v3/max_fs = 127
bad_p9v3/dim1 = 9
bad_p9v3/dim2 = ss
bad_p9v3/dim3 = fs

bad_p9v4/min_ss = 187
bad_p9v4/min_fs = 0
bad_p9v4/max_ss = 196
bad_p9v4/max_fs = 127
bad_p9v4/dim1 = 9
bad_p9v4/dim2 = ss
bad_p9v4/dim3 = fs

bad_p9v5/min_ss = 251
bad_p9v5/min_fs = 0
bad_p9v5/max_ss = 260
bad_p9v5/max_fs = 127
bad_p9v5/dim1 = 9
bad_p9v5/dim2 = ss
bad_p9v5/dim3 = fs

bad_p9v6/min_ss = 315
bad_p9v6/min_fs = 0
bad_p9v6/max_ss = 324
bad_p9v6/max_fs = 127
bad_p9v6/dim1 = 9
bad_p9v6/dim2 = ss
bad_p9v6/dim3 = fs

bad_p9v7/min_ss = 379
bad_p9v7/min_fs = 0
bad_p9v7/max_ss = 388
bad_p9v7/max_fs = 127
bad_p9v7/dim1 = 9
bad_p9v7/dim2 = ss
bad_p9v7/dim3 = fs

bad_p9v8/min_ss = 443
bad_p9v8/min_fs = 0
bad_p9v8/max_ss = 452
bad_p9v8/max_fs = 127
bad_p9v8/dim1 = 9
bad_p9v8/dim2 = ss
bad_p9v8/dim3 = fs

bad_p9v9/min_ss = 507
bad_p9v9/min_fs = 0
bad_p9v9/max_ss = 511
bad_p9v9/max_fs = 127
bad_p9v9/dim1 = 9
bad_p9v9/dim2 = ss
bad_p9v9/dim3 = fs
bad_p10h1/min_ss = 0
bad_p10h1/min_fs = 0
bad_p10h1/max_ss = 511
bad_p10h1/max_fs = 4
bad_p10h1/dim1 = 10
bad_p10h1/dim2 = ss
bad_p10h1/dim3 = fs

bad_p10h2/min_ss = 0
bad_p10h2/min_fs = 123
bad_p10h2/max_ss = 511
bad_p10h2/max_fs = 127
bad_p10h2/dim1 = 10
bad_p10h2/dim2 = ss
bad_p10h2/dim3 = fs

bad_p10v1/min_ss = 0
bad_p10v1/min_fs = 0
bad_p10v1/max_ss = 4
bad_p10v1/max_fs = 127
bad_p10v1/dim1 = 10
bad_p10v1/dim2 = ss
bad_p10v1/dim3 = fs

bad_p10v2/min_ss = 59
bad_p10v2/min_fs = 0
bad_p10v2/max_ss = 68
bad_p10v2/max_fs = 127
bad_p10v2/dim1 = 10
bad_p10v2/dim2 = ss
bad_p10v2/dim3 = fs

bad_p10v3/min_ss = 123
bad_p10v3/min_fs = 0
bad_p10v3/max_ss = 132
bad_p10v3/max_fs = 127
bad_p10v3/dim1 = 10
bad_p10v3/dim2 = ss
bad_p10v3/dim3 = fs

bad_p10v4/min_ss = 187
bad_p10v4/min_fs = 0
bad_p10v4/max_ss = 196
bad_p10v4/max_fs = 127
bad_p10v4/dim1 = 10
bad_p10v4/dim2 = ss
bad_p10v4/dim3 = fs

bad_p10v5/min_ss = 251
bad_p10v5/min_fs = 0
bad_p10v5/max_ss = 260
bad_p10v5/max_fs = 127
bad_p10v5/dim1 = 10
bad_p10v5/dim2 = ss
bad_p10v5/dim3 = fs

bad_p10v6/min_ss = 315
bad_p10v6/min_fs = 0
bad_p10v6/max_ss = 324
bad_p10v6/max_fs = 127
bad_p10v6/dim1 = 10
bad_p10v6/dim2 = ss
bad_p10v6/dim3 = fs

bad_p10v7/min_ss = 379
bad_p10v7/min_fs = 0
bad_p10v7/max_ss = 388
bad_p10v7/max_fs = 127
bad_p10v7/dim1 = 10
bad_p10v7/dim2 = ss
bad_p10v7/dim3 = fs

bad_p10v8/min_ss = 443
bad_p10v8/min_fs = 0
bad_p10v8/max_ss = 452
bad_p10v8/max_fs = 127
bad_p10v8/dim1 = 10
bad_p10v8/dim2 = ss
bad_p10v8/dim3 = fs

bad_p10v9/min_ss = 507
bad_p10v9/min_fs = 0
bad_p10v9/max_ss = 511
bad_p10v9/max_fs = 127
bad_p10v9/dim1 = 10
bad_p10v9/dim2 = ss
bad_p10v9/dim3 = fs
bad_p11h1/min_ss = 0
bad_p11h1/min_fs = 0
bad_p11h1/max_ss = 511
bad_p11h1/max_fs = 4
bad_p11h1/dim1 = 11
bad_p11h1/dim2 = ss
bad_p11h1/dim3 = fs

bad_p11h2/min_ss = 0
bad_p11h2/min_fs = 123
bad_p11h2/max_ss = 511
bad_p11h2/max_fs = 127
bad_p11h2/dim1 = 11
bad_p11h2/dim2 = ss
bad_p11h2/dim3 = fs

bad_p11v1/min_ss = 0
bad_p11v1/min_fs = 0
bad_p11v1/max_ss = 4
bad_p11v1/max_fs = 127
bad_p11v1/dim1 = 11
bad_p11v1/dim2 = ss
bad_p11v1/dim3 = fs

bad_p11v2/min_ss = 59
bad_p11v2/min_fs = 0
bad_p11v2/max_ss = 68
bad_p11v2/max_fs = 127
bad_p11v2/dim1 = 11
bad_p11v2/dim2 = ss
bad_p11v2/dim3 = fs

bad_p11v3/min_ss = 123
bad_p11v3/min_fs = 0
bad_p11v3/max_ss = 132
bad_p11v3/max_fs = 127
bad_p11v3/dim1 = 11
bad_p11v3/dim2 = ss
bad_p11v3/dim3 = fs

bad_p11v4/min_ss = 187
bad_p11v4/min_fs = 0
bad_p11v4/max_ss = 196
bad_p11v4/max_fs = 127
bad_p11v4/dim1 = 11
bad_p11v4/dim2 = ss
bad_p11v4/dim3 = fs

bad_p11v5/min_ss = 251
bad_p11v5/min_fs = 0
bad_p11v5/max_ss = 260
bad_p11v5/max_fs = 127
bad_p11v5/dim1 = 11
bad_p11v5/dim2 = ss
bad_p11v5/dim3 = fs

bad_p11v6/min_ss = 315
bad_p11v6/min_fs = 0
bad_p11v6/max_ss = 324
bad_p11v6/max_fs = 127
bad_p11v6/dim1 = 11
bad_p11v6/dim2 = ss
bad_p11v6/dim3 = fs

bad_p11v7/min_ss = 379
bad_p11v7/min_fs = 0
bad_p11v7/max_ss = 388
bad_p11v7/max_fs = 127
bad_p11v7/dim1 = 11
bad_p11v7/dim2 = ss
bad_p11v7/dim3 = fs

bad_p11v8/min_ss = 443
bad_p11v8/min_fs = 0
bad_p11v8/max_ss = 452
bad_p11v8/max_fs = 127
bad_p11v8/dim1 = 11
bad_p11v8/dim2 = ss
bad_p11v8/dim3 = fs

bad_p11v9/min_ss = 507
bad_p11v9/min_fs = 0
bad_p11v9/max_ss = 511
bad_p11v9/max_fs = 127
bad_p11v9/dim1 = 11
bad_p11v9/dim2 = ss
bad_p11v9/dim3 = fs
bad_p12h1/min_ss = 0
bad_p12h1/min_fs = 0
bad_p12h1/max_ss = 511
bad_p12h1/max_fs = 4
bad_p12h1/dim1 = 12
bad_p12h1/dim2 = ss
bad_p12h1/dim3 = fs

bad_p12h2/min_ss = 0
bad_p12h2/min_fs = 123
bad_p12h2/max_ss = 511
bad_p12h2/max_fs = 127
bad_p12h2/dim1 = 12
bad_p12h2/dim2 = ss
bad_p12h2/dim3 = fs

bad_p12v1/min_ss = 0
bad_p12v1/min_fs = 0
bad_p12v1/max_ss = 4
bad_p12v1/max_fs = 127
bad_p12v1/dim1 = 12
bad_p12v1/dim2 = ss
bad_p12v1/dim3 = fs

bad_p12v2/min_ss = 59
bad_p12v2/min_fs = 0
bad_p12v2/max_ss = 68
bad_p12v2/max_fs = 127
bad_p12v2/dim1 = 12
bad_p12v2/dim2 = ss
bad_p12v2/dim3 = fs

bad_p12v3/min_ss = 123
bad_p12v3/min_fs = 0
bad_p12v3/max_ss = 132
bad_p12v3/max_fs = 127
bad_p12v3/dim1 = 12
bad_p12v3/dim2 = ss
bad_p12v3/dim3 = fs

bad_p12v4/min_ss = 187
bad_p12v4/min_fs = 0
bad_p12v4/max_ss = 196
bad_p12v4/max_fs = 127
bad_p12v4/dim1 = 12
bad_p12v4/dim2 = ss
bad_p12v4/dim3 = fs

bad_p12v5/min_ss = 251
bad_p12v5/min_fs = 0
bad_p12v5/max_ss = 260
bad_p12v5/max_fs = 127
bad_p12v5/dim1 = 12
bad_p12v5/dim2 = ss
bad_p12v5/dim3 = fs

bad_p12v6/min_ss = 315
bad_p12v6/min_fs = 0
bad_p12v6/max_ss = 324
bad_p12v6/max_fs = 127
bad_p12v6/dim1 = 12
bad_p12v6/dim2 = ss
bad_p12v6/dim3 = fs

bad_p12v7/min_ss = 379
bad_p12v7/min_fs = 0
bad_p12v7/max_ss = 388
bad_p12v7/max_fs = 127
bad_p12v7/dim1 = 12
bad_p12v7/dim2 = ss
bad_p12v7/dim3 = fs

bad_p12v8/min_ss = 443
bad_p12v8/min_fs = 0
bad_p12v8/max_ss = 452
bad_p12v8/max_fs = 127
bad_p12v8/dim1 = 12
bad_p12v8/dim2 = ss
bad_p12v8/dim3 = fs

bad_p12v9/min_ss = 507
bad_p12v9/min_fs = 0
bad_p12v9/max_ss = 511
bad_p12v9/max_fs = 127
bad_p12v9/dim1 = 12
bad_p12v9/dim2 = ss
bad_p12v9/dim3 = fs
bad_p13h1/min_ss = 0
bad_p13h1/min_fs = 0
bad_p13h1/max_ss = 511
bad_p13h1/max_fs = 4
bad_p13h1/dim1 = 13
bad_p13h1/dim2 = ss
bad_p13h1/dim3 = fs

bad_p13h2/min_ss = 0
bad_p13h2/min_fs = 123
bad_p13h2/max_ss = 511
bad_p13h2/max_fs = 127
bad_p13h2/dim1 = 13
bad_p13h2/dim2 = ss
bad_p13h2/dim3 = fs

bad_p13v1/min_ss = 0
bad_p13v1/min_fs = 0
bad_p13v1/max_ss = 4
bad_p13v1/max_fs = 127
bad_p13v1/dim1 = 13
bad_p13v1/dim2 = ss
bad_p13v1/dim3 = fs

bad_p13v2/min_ss = 59
bad_p13v2/min_fs = 0
bad_p13v2/max_ss = 68
bad_p13v2/max_fs = 127
bad_p13v2/dim1 = 13
bad_p13v2/dim2 = ss
bad_p13v2/dim3 = fs

bad_p13v3/min_ss = 123
bad_p13v3/min_fs = 0
bad_p13v3/max_ss = 132
bad_p13v3/max_fs = 127
bad_p13v3/dim1 = 13
bad_p13v3/dim2 = ss
bad_p13v3/dim3 = fs

bad_p13v4/min_ss = 187
bad_p13v4/min_fs = 0
bad_p13v4/max_ss = 196
bad_p13v4/max_fs = 127
bad_p13v4/dim1 = 13
bad_p13v4/dim2 = ss
bad_p13v4/dim3 = fs

bad_p13v5/min_ss = 251
bad_p13v5/min_fs = 0
bad_p13v5/max_ss = 260
bad_p13v5/max_fs = 127
bad_p13v5/dim1 = 13
bad_p13v5/dim2 = ss
bad_p13v5/dim3 = fs

bad_p13v6/min_ss = 315
bad_p13v6/min_fs = 0
bad_p13v6/max_ss = 324
bad_p13v6/max_fs = 127
bad_p13v6/dim1 = 13
bad_p13v6/dim2 = ss
bad_p13v6/dim3 = fs

bad_p13v7/min_ss = 379
bad_p13v7/min_fs = 0
bad_p13v7/max_ss = 388
bad_p13v7/max_fs = 127
bad_p13v7/dim1 = 13
bad_p13v7/dim2 = ss
bad_p13v7/dim3 = fs

bad_p13v8/min_ss = 443
bad_p13v8/min_fs = 0
bad_p13v8/max_ss = 452
bad_p13v8/max_fs = 127
bad_p13v8/dim1 = 13
bad_p13v8/dim2 = ss
bad_p13v8/dim3 = fs

bad_p13v9/min_ss = 507
bad_p13v9/min_fs = 0
bad_p13v9/max_ss = 511
bad_p13v9/max_fs = 127
bad_p13v9/dim1 = 13
bad_p13v9/dim2 = ss
bad_p13v9/dim3 = fs
bad_p14h1/min_ss = 0
bad_p14h1/min_fs = 0
bad_p14h1/max_ss = 511
bad_p14h1/max_fs = 4
bad_p14h1/dim1 = 14
bad_p14h1/dim2 = ss
bad_p14h1/dim3 = fs

bad_p14h2/min_ss = 0
bad_p14h2/min_fs = 123
bad_p14h2/max_ss = 511
bad_p14h2/max_fs = 127
bad_p14h2/dim1 = 14
bad_p14h2/dim2 = ss
bad_p14h2/dim3 = fs

bad_p14v1/min_ss = 0
bad_p14v1/min_fs = 0
bad_p14v1/max_ss = 4
bad_p14v1/max_fs = 127
bad_p14v1/dim1 = 14
bad_p14v1/dim2 = ss
bad_p14v1/dim3 = fs

bad_p14v2/min_ss = 59
bad_p14v2/min_fs = 0
bad_p14v2/max_ss = 68
bad_p14v2/max_fs = 127
bad_p14v2/dim1 = 14
bad_p14v2/dim2 = ss
bad_p14v2/dim3 = fs

bad_p14v3/min_ss = 123
bad_p14v3/min_fs = 0
bad_p14v3/max_ss = 132
bad_p14v3/max_fs = 127
bad_p14v3/dim1 = 14
bad_p14v3/dim2 = ss
bad_p14v3/dim3 = fs

bad_p14v4/min_ss = 187
bad_p14v4/min_fs = 0
bad_p14v4/max_ss = 196
bad_p14v4/max_fs = 127
bad_p14v4/dim1 = 14
bad_p14v4/dim2 = ss
bad_p14v4/dim3 = fs

bad_p14v5/min_ss = 251
bad_p14v5/min_fs = 0
bad_p14v5/max_ss = 260
bad_p14v5/max_fs = 127
bad_p14v5/dim1 = 14
bad_p14v5/dim2 = ss
bad_p14v5/dim3 = fs

bad_p14v6/min_ss = 315
bad_p14v6/min_fs = 0
bad_p14v6/max_ss = 324
bad_p14v6/max_fs = 127
bad_p14v6/dim1 = 14
bad_p14v6/dim2 = ss
bad_p14v6/dim3 = fs

bad_p14v7/min_ss = 379
bad_p14v7/min_fs = 0
bad_p14v7/max_ss = 388
bad_p14v7/max_fs = 127
bad_p14v7/dim1 = 14
bad_p14v7/dim2 = ss
bad_p14v7/dim3 = fs

bad_p14v8/min_ss = 443
bad_p14v8/min_fs = 0
bad_p14v8/max_ss = 452
bad_p14v8/max_fs = 127
bad_p14v8/dim1 = 14
bad_p14v8/dim2 = ss
bad_p14v8/dim3 = fs

bad_p14v9/min_ss = 507
bad_p14v9/min_fs = 0
bad_p14v9/max_ss = 511
bad_p14v9/max_fs = 127
bad_p14v9/dim1 = 14
bad_p14v9/dim2 = ss
bad_p14v9/dim3 = fs
bad_p15h1/min_ss = 0
bad_p15h1/min_fs = 0
bad_p15h1/max_ss = 511
bad_p15h1/max_fs = 4
bad_p15h1/dim1 = 15
bad_p15h1/dim2 = ss
bad_p15h1/dim3 = fs

bad_p15h2/min_ss = 0
bad_p15h2/min_fs = 123
bad_p15h2/max_ss = 511
bad_p15h2/max_fs = 127
bad_p15h2/dim1 = 15
bad_p15h2/dim2 = ss
bad_p15h2/dim3 = fs

bad_p15v1/min_ss = 0
bad_p15v1/min_fs = 0
bad_p15v1/max_ss = 4
bad_p15v1/max_fs = 127
bad_p15v1/dim1 = 15
bad_p15v1/dim2 = ss
bad_p15v1/dim3 = fs

bad_p15v2/min_ss = 59
bad_p15v2/min_fs = 0
bad_p15v2/max_ss = 68
bad_p15v2/max_fs = 127
bad_p15v2/dim1 = 15
bad_p15v2/dim2 = ss
bad_p15v2/dim3 = fs

bad_p15v3/min_ss = 123
bad_p15v3/min_fs = 0
bad_p15v3/max_ss = 132
bad_p15v3/max_fs = 127
bad_p15v3/dim1 = 15
bad_p15v3/dim2 = ss
bad_p15v3/dim3 = fs

bad_p15v4/min_ss = 187
bad_p15v4/min_fs = 0
bad_p15v4/max_ss = 196
bad_p15v4/max_fs = 127
bad_p15v4/dim1 = 15
bad_p15v4/dim2 = ss
bad_p15v4/dim3 = fs

bad_p15v5/min_ss = 251
bad_p15v5/min_fs = 0
bad_p15v5/max_ss = 260
bad_p15v5/max_fs = 127
bad_p15v5/dim1 = 15
bad_p15v5/dim2 = ss
bad_p15v5/dim3 = fs

bad_p15v6/min_ss = 315
bad_p15v6/min_fs = 0
bad_p15v6/max_ss = 324
bad_p15v6/max_fs = 127
bad_p15v6/dim1 = 15
bad_p15v6/dim2 = ss
bad_p15v6/dim3 = fs

bad_p15v7/min_ss = 379
bad_p15v7/min_fs = 0
bad_p15v7/max_ss = 388
bad_p15v7/max_fs = 127
bad_p15v7/dim1 = 15
bad_p15v7/dim2 = ss
bad_p15v7/dim3 = fs

bad_p15v8/min_ss = 443
bad_p15v8/min_fs = 0
bad_p15v8/max_ss = 452
bad_p15v8/max_fs = 127
bad_p15v8/dim1 = 15
bad_p15v8/dim2 = ss
bad_p15v8/dim3 = fs

bad_p15v9/min_ss = 507
bad_p15v9/min_fs = 0
bad_p15v9/max_ss = 511
bad_p15v9/max_fs = 127
bad_p15v9/dim1 = 15
bad_p15v9/dim2 = ss
bad_p15v9/dim3 = fs
