; Manually optimized with hdfsee
; Manually optimized with hdfsee
; Manually optimized with hdfsee
; Manually optimized with hdfsee
; Manually optimized with hdfsee
; Example geometry file for Eiger 16M detector, using its native file format
; and binning 2.

; Camera length (in m) and photon energy (eV)

clen = 0.1996 ;0.1995 ;0.200 

photon_energy = 12000 ;12050
;max_adu = 100000

; adu_per_photon needs a relatively recent CrystFEL version.  If your version is
; older, change it to adu_per_eV and set it to one over the photon energy in eV
adu_per_photon = 1
res = 13333.3   ; 75 micron pixel size

; These lines describe the data layout for the Eiger native multi-event files
dim0 = %
dim1 = ss
dim2 = fs
data = /entry/data/data

;peak_info_location = /entry_1/result_1

;beamstop
;bad_b1/min_fs = 0
;bad_b1/min_ss = 1003
;bad_b1/max_fs = 1100
;bad_b1/max_ss = 1123

; Uncomment these lines if you have a separate bad pixel map (recommended!)
;mask_file = /asap3/petra3/gpfs/p11/2021/data/11010507/scratch_cc/galchenm/mask_thick_v0.h5
;mask = /data/data
mask_good = 0x1
mask_bad = 0x0


rigid_group_d0 = panel0
rigid_group_collection_det = d0

; corner_{x,y} set the position of the corner of the detector (in pixels)
; relative to the beam

panel0/min_fs = 0 
panel0/min_ss = 0 
panel0/max_fs = 4147
panel0/max_ss = 4361
panel0/corner_x = -2130.346392
panel0/corner_y = -2184.369105
panel0/fs = +1.000000x +0.000000y 
panel0/ss = +0.000000x +1.000000y



