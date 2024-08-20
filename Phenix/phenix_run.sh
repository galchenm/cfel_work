source /etc/profile.d/modules.sh
module load phenix/1.13
module load xray

INPUT_FOR_MTZ=$1
RES=$2
BINS=10  # $3

cp /gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/Phenix_files/lyz/create-mtz-422 .
chmod +x create-mtz-422
source ./create-mtz-422 $INPUT_FOR_MTZ


name_of_job=$(echo $(basename $INPUT_FOR_MTZ))
name_of_job=$(echo ${name_of_job%.*})

cp /gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/Phenix_files/lyz/6ftr.pdb .
cp /gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/Phenix_files/lyz/6FTR.mtz .
cp /gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/Phenix_files/lyz/parameter_lys ./parameter_lys_${name_of_job}.eff


sed -i "s/output_file = N/output_file = rfree_lys_${name_of_job}.mtz/g" parameter_lys_${name_of_job}.eff
sed -i "s/file_name = M/file_name = ${name_of_job}.mtz/g" parameter_lys_${name_of_job}.eff
iotbx.reflection_file_editor parameter_lys_${name_of_job}.eff
cp /gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/Phenix_files/lyz/refine_param_lys ./refine_param_lys_${name_of_job}.eff
sed -i "s/refine_NXC/refine_param_lys_${name_of_job}/g" refine_param_lys_${name_of_job}.eff

phenix.refine rfree_lys_${name_of_job}.mtz 6ftr.pdb refine_param_lys_${name_of_job}.eff  xray_data.high_resolution=${RES} output.n_resolution_bins=${BINS} --unused_ok