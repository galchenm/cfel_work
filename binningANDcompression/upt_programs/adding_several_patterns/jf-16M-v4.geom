; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
;adu_per_eV = 0.00022222
adu_per_photon = 1
res = 13333.3  
clen = 0.0956 ;0.0955 ;0.0952
photon_energy = 4570

dim0 = %
dim1 = ss
dim2 = fs
data = /data/data

rigid_group_m0 = m0
rigid_group_m1 = m1
rigid_group_m2 = m2
rigid_group_m3 = m3
rigid_group_m4 = m4
rigid_group_m5 = m5
rigid_group_m6 = m6
rigid_group_m7 = m7
rigid_group_m8 = m8
rigid_group_m9 = m9
rigid_group_m10 = m10
rigid_group_m11 = m11
rigid_group_m12 = m12
rigid_group_m13 = m13
rigid_group_m14 = m14
rigid_group_m15 = m15
rigid_group_m16 = m16
rigid_group_m17 = m17
rigid_group_m18 = m18
rigid_group_m19 = m19
rigid_group_m20 = m20
rigid_group_m21 = m21
rigid_group_m22 = m22
rigid_group_m23 = m23
rigid_group_m24 = m24
rigid_group_m25 = m25
rigid_group_m26 = m26
rigid_group_m27 = m27
rigid_group_m28 = m28
rigid_group_m29 = m29
rigid_group_m30 = m30
rigid_group_m31 = m31

rigid_group_collection_myrg = m0,m1,m2,m3,m4,m5,m6,m7,m8,m9,m10,m11,m12,m13,m14,m15,m16,m17,m18,m19,m20,m21,m22,m23,m24,m25,m26,m27,m28,m29,m30,m31

mask_file = mask_common_16M.h5 ;/gpfs/exfel/u/scratch/SPB/202002/p002442/galchenm/processed/blocks/SAD/thau/mask_v1.h5
;mask = /mask
mask = /data/data
mask_good = 0x1
mask_bad = 0x0


;square in the center
;badregionb/min_x = -100
;badregionb/max_x = 100
;badregionb/min_y = -100
;badregionb/max_y = 100

;top lines from center
;badregionc/min_x = -12
;badregionc/max_x = -56
;badregionc/min_y = -10
;badregionc/max_y = 820

;bottom lines from center
;badregiond/min_x = 55
;badregiond/max_x = 13
;badregiond/min_y = -810
;badregiond/max_y = 20

m0/min_fs = 0
m0/min_ss = 0
m0/max_fs = 1029
m0/max_ss = 513
m0/fs = +0.002744x -0.999927y
m0/ss = -0.998974x -0.002449y
m0/corner_x = 2140.24
m0/corner_y = 1130.32
 
m1/min_fs = 0
m1/min_ss = 514
m1/max_fs = 1029
m1/max_ss = 1027
m1/fs = +0.001021x -0.999741y
m1/ss = -0.999217x -0.001015y
m1/corner_x = 2207.78
m1/corner_y = 92.6697
 
m2/min_fs = 0
m2/min_ss = 1028
m2/max_fs = 1029
m2/max_ss = 1541
m2/fs = -0.000088x -1.000537y
m2/ss = -0.998342x -0.000899y
m2/corner_x = 1593.15
m2/corner_y = 2100.35
 
m3/min_fs = 0
m3/min_ss = 1542
m3/max_fs = 1029
m3/max_ss = 2055
m3/fs = +0.002123x -0.999779y
m3/ss = -0.998293x -0.002310y
m3/corner_x = 1593.87
m3/corner_y = 1063.89
 
m4/min_fs = 0
m4/min_ss = 2056
m4/max_fs = 1029
m4/max_ss = 2569
m4/fs = -0.000233x -0.999418y
m4/ss = -0.999854x +0.000743y
m4/corner_x = 1664.66
m4/corner_y = 24.3112
 
m5/min_fs = 0
m5/min_ss = 2570
m5/max_fs = 1029
m5/max_ss = 3083
m5/fs = +0.005256x -1.000410y
m5/ss = -1.000828x -0.003859y
m5/corner_x = 1660.66
m5/corner_y = -1010.86
 
m6/min_fs = 0
m6/min_ss = 3084
m6/max_fs = 1029
m6/max_ss = 3597
m6/fs = -0.001852x -0.999791y
m6/ss = -0.998787x +0.000292y
m6/corner_x = 1046.48
m6/corner_y = 2102.82
 
m7/min_fs = 0
m7/min_ss = 3598
m7/max_fs = 1029
m7/max_ss = 4111
m7/fs = +0.000924x -1.000012y
m7/ss = -0.999832x -0.000807y
m7/corner_x = 1046.91
m7/corner_y = 1065.15
 
m8/min_fs = 0
m8/min_ss = 4112
m8/max_fs = 1029
m8/max_ss = 4625
m8/fs = +0.000608x -0.999939y
m8/ss = -0.999456x -0.000774y
m8/corner_x = 1114.63
m8/corner_y = 24.9613
 
m9/min_fs = 0
m9/min_ss = 4626
m9/max_fs = 1029
m9/max_ss = 5139
m9/fs = -0.002896x -0.999950y
m9/ss = -0.999930x +0.004046y
m9/corner_x = 1113
m9/corner_y = -1015.38
 
m10/min_fs = 0
m10/min_ss = 5140
m10/max_fs = 1029
m10/max_ss = 5653
m10/fs = -0.001640x -0.998347y
m10/ss = -1.000118x +0.001333y
m10/corner_x = 498.123
m10/corner_y = 2101.47
 
m11/min_fs = 0
m11/min_ss = 5654
m11/max_fs = 1029
m11/max_ss = 6167
m11/fs = +0.000171x -1.000221y
m11/ss = -1.000519x -0.000007y
m11/corner_x = 496.906
m11/corner_y = 1065.86
 
m12/min_fs = 0
m12/min_ss = 6168
m12/max_fs = 1029
m12/max_ss = 6681
m12/fs = -0.000592x -0.999919y
m12/ss = -1.000472x +0.000242y
m12/corner_x = 564.97
m12/corner_y = 24.4069
 
m13/min_fs = 0
m13/min_ss = 6682
m13/max_fs = 1029
m13/max_ss = 7195
m13/fs = -0.001555x -0.999837y
m13/ss = -1.000381x +0.001288y
m13/corner_x = 563.731
m13/corner_y = -1014.69
 
m14/min_fs = 0
m14/min_ss = 7196
m14/max_fs = 1029
m14/max_ss = 7709
m14/fs = -0.001613x -0.999947y
m14/ss = -0.999713x +0.001803y
m14/corner_x = -52.2874
m14/corner_y = 2035.06
 
m15/min_fs = 0
m15/min_ss = 7710
m15/max_fs = 1029
m15/max_ss = 8223
m15/fs = -0.000202x -1.000300y
m15/ss = -1.000175x +0.000063y
m15/corner_x = -53.0042
m15/corner_y = 998.251
 
m16/min_fs = 0
m16/min_ss = 8224
m16/max_fs = 1029
m16/max_ss = 8737
m16/fs = -0.000576x -0.999887y
m16/ss = -1.000175x +0.000515y
m16/corner_x = 14.8633
m16/corner_y = -42.6525
 
m17/min_fs = 0
m17/min_ss = 8738
m17/max_fs = 1029
m17/max_ss = 9251
m17/fs = +0.000071x -0.999999y
m17/ss = -0.999999x -0.000071y
m17/corner_x = 14.7173
m17/corner_y = -1079.92
 
m18/min_fs = 0
m18/min_ss = 9252
m18/max_fs = 1029
m18/max_ss = 9765
m18/fs = -0.002215x -0.999463y
m18/ss = -0.999374x +0.003710y
m18/corner_x = -600.261
m18/corner_y = 2033.6
 
m19/min_fs = 0
m19/min_ss = 9766
m19/max_fs = 1029
m19/max_ss = 10279
m19/fs = +0.000603x -1.000051y
m19/ss = -0.998685x -0.000698y
m19/corner_x = -603.921
m19/corner_y = 997.939
 
m20/min_fs = 0
m20/min_ss = 10280
m20/max_fs = 1029
m20/max_ss = 10793
m20/fs = +0.001122x -0.999711y
m20/ss = -0.999193x -0.001230y
m20/corner_x = -535.966
m20/corner_y = -41.8642
 
m21/min_fs = 0
m21/min_ss = 10794
m21/max_fs = 1029
m21/max_ss = 11307
m21/fs = -0.000282x -1.000040y
m21/ss = -0.999010x -0.001413y
m21/corner_x = -534.133
m21/corner_y = -1079.67
 
m22/min_fs = 0
m22/min_ss = 11308
m22/max_fs = 1029
m22/max_ss = 11821
m22/fs = -0.003078x -1.001682y
m22/ss = -0.998398x +0.003293y
m22/corner_x = -1146.23
m22/corner_y = 2033.78
 
m23/min_fs = 0
m23/min_ss = 11822
m23/max_fs = 1029
m23/max_ss = 12335
m23/fs = +0.002069x -0.999641y
m23/ss = -0.999211x -0.001634y
m23/corner_x = -1152.33
m23/corner_y = 996.75
 
m24/min_fs = 0
m24/min_ss = 12336
m24/max_fs = 1029
m24/max_ss = 12849
m24/fs = +0.002633x -0.999276y
m24/ss = -0.999424x -0.002834y
m24/corner_x = -1085.24
m24/corner_y = -41.3985
 
m25/min_fs = 0
m25/min_ss = 12850
m25/max_fs = 1029
m25/max_ss = 13363
m25/fs = +0.000796x -0.999947y
m25/ss = -0.999947x -0.002006y
m25/corner_x = -1081.42
m25/corner_y = -1077.56
 
m26/min_fs = 0
m26/min_ss = 13364
m26/max_fs = 1029
m26/max_ss = 13877
m26/fs = +0.004002x -0.996833y
m26/ss = -1.001362x -0.000471y
m26/corner_x = -1707.24
m26/corner_y = 2033.08
 
m27/min_fs = 0
m27/min_ss = 13878
m27/max_fs = 1029
m27/max_ss = 14391
m27/fs = +0.004249x -0.999525y
m27/ss = -0.998738x -0.004102y
m27/corner_x = -1700.06
m27/corner_y = 996.632
 
m28/min_fs = 0
m28/min_ss = 14392
m28/max_fs = 1029
m28/max_ss = 14905
m28/fs = +0.005298x -0.999589y
m28/ss = -0.999250x -0.005979y
m28/corner_x = -1631.37
m28/corner_y = -40.0838
 
m29/min_fs = 0
m29/min_ss = 14906
m29/max_fs = 1029
m29/max_ss = 15419
m29/fs = +0.000400x -1.001056y
m29/ss = -0.998514x -0.000848y
m29/corner_x = -1630.65
m29/corner_y = -1077.65
 
m30/min_fs = 0
m30/min_ss = 15420
m30/max_fs = 1029
m30/max_ss = 15933
m30/fs = +0.000071x -0.999999y
m30/ss = -0.999999x -0.000071y
m30/corner_x = -2252.28
m30/corner_y = 997.454
 
m31/min_fs = 0
m31/min_ss = 15934
m31/max_fs = 1029
m31/max_ss = 16447
m31/fs = +0.000071x -0.999999y
m31/ss = -0.999999x -0.000071y
m31/corner_x = -2183.37
m31/corner_y = -41.1583
 

