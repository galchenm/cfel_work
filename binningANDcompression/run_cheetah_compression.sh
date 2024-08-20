#!/bin/sh

module load anaconda3/5.2

run=$1

#outdir=/asap3/petra3/gpfs/p11/2020/data/11010575/scratch_cc/galchenm/compression/${run}-compressed
outdir=$2

if [[ ! -e $outdir ]]; then
    mkdir $outdir
elif [[ ! -d $outdir ]]; then
    echo "$outdir already exists but is not a directory" 1>&2
fi

cd $outdir

#find  /asap3/petra3/gpfs/p11/2020/data/11009046/raw/${run} -name "*_data_*.h5" > files.lst
find /asap3/petra3/gpfs/p11/2020/data/11010575/raw/${run} -name "*_data_*.h5" > files.lst

cp /gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/template.yaml monitor.yaml

sed -i "s/RUN/$run/" monitor.yaml

SLURMFILE="${run}.sh"

echo "#!/bin/sh" > $SLURMFILE
echo >> $SLURMFILE

echo "#SBATCH --partition=upex" >> $SLURMFILE  # Set your partition here
echo "#SBATCH --time=24:00:00" >> $SLURMFILE
echo "#SBATCH --nodes=1" >> $SLURMFILE
echo >> $SLURMFILE

echo "#SBATCH --chdir   $outdir" >> $SLURMFILE
echo "#SBATCH --job-name  ${run}-cheetah" >> $SLURMFILE
echo "#SBATCH --output    ${outdir}/slurm.out" >> $SLURMFILE
echo "#SBATCH --error     ${outdir}/slurm.err" >> $SLURMFILE
echo "#SBATCH --nice=100" >> $SLURMFILE

echo >> $SLURMFILE

echo "module load anaconda3/5.2" >> $SLURMFILE
echo "export PATH=$PATH:/asap3/petra3/gpfs/p11/2020/data/11009046/scratch_cc/alexandra/cheetah/bin/" >> $SLURMFILE
echo "export PYTHONPATH=$PYTHONPATH:/asap3/petra3/gpfs/p11/2020/data/11009046/scratch_cc/alexandra/cheetah/lib/python3.6/site-packages/" >> $SLURMFILE
echo "mpirun -np 30 /asap3/petra3/gpfs/p11/2020/data/11009046/scratch_cc/alexandra/cheetah/bin/om_monitor.py ${outdir}/files.lst" >> $SLURMFILE

sbatch $SLURMFILE

cd /gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/