; 
; Optimized panel offsets can be found at the end of the file
photon_energy = 11500 ;11560 eV    ; dependent of the experiment, can be imported from a HDF5 file
photon_energy_bandwidth = 0.01
; adu_per_eV = 8.6505-05 ; dependent of the experiment (equal to 1 over photon energy in eV)
adu_per_photon = 1       ; use it instead of adu_per_eV
clen = 0.1766 ;0.1756 ;0.1771 ;0.1766 ;0.1767 ;0.1768 ;0.1766 ;0.177 ;0.17738 ;0.176446
res = 13333.3            ; 75 micron pixel size

flag_morethan = 2100000000

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

rigid_group_detector = detector
rigid_group_collection_detector = detector

detector/min_fs = 0
detector/max_fs = 2067
detector/min_ss = 0
detector/max_ss = 2163
detector/fs = +1.000000x +0.000063y
detector/ss = -0.000063x +1.000000y
detector/corner_x = -1053.03
detector/corner_y = -1131.35


;bad_LCP/min_fs = 980
;bad_LCP/min_ss = 1100
;bad_LCP/max_fs = 1110
;bad_LCP/max_ss = 1210

bad_v_0/min_fs = 256
bad_v_0/min_ss = 0
bad_v_0/max_fs = 257
bad_v_0/max_ss = 2163

bad_v_1/min_fs = 514
bad_v_1/min_ss = 0
bad_v_1/max_fs = 515
bad_v_1/max_ss = 2163

bad_v_2/min_fs = 772
bad_v_2/min_ss = 0
bad_v_2/max_fs = 773
bad_v_2/max_ss = 2163

bad_v_3/min_fs = 1030
bad_v_3/min_ss = 0
bad_v_3/max_fs = 1037
bad_v_3/max_ss = 2163

bad_v_4/min_fs = 1294
bad_v_4/min_ss = 0
bad_v_4/max_fs = 1295
bad_v_4/max_ss = 2163

bad_v_5/min_fs = 1552
bad_v_5/min_ss = 0
bad_v_5/max_fs = 1553
bad_v_5/max_ss = 2163

bad_v_6/min_fs = 1810
bad_v_6/min_ss = 0
bad_v_6/max_fs = 1811
bad_v_6/max_ss = 2163

bad_h_0/min_fs = 0
bad_h_0/min_ss = 256
bad_h_0/max_fs = 2067
bad_h_0/max_ss = 257

bad_h_1/min_fs = 0
bad_h_1/min_ss = 514
bad_h_1/max_fs = 2067
bad_h_1/max_ss = 549

bad_h_2/min_fs = 0
bad_h_2/min_ss = 806
bad_h_2/max_fs = 2067
bad_h_2/max_ss = 807

bad_h_3/min_fs = 0
bad_h_3/min_ss = 1064
bad_h_3/max_fs = 2067
bad_h_3/max_ss = 1099

bad_h_4/min_fs = 0
bad_h_4/min_ss = 1356
bad_h_4/max_fs = 2067
bad_h_4/max_ss = 1357

bad_h_5/min_fs = 0
bad_h_5/min_ss = 1614
bad_h_5/max_fs = 2067
bad_h_5/max_ss = 1649

bad_h_6/min_fs = 0
bad_h_6/min_ss = 1906
bad_h_6/max_fs = 2067
bad_h_6/max_ss = 1907


detector/coffset = -0.000118
