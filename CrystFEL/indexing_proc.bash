#!/bin/bash

# Split a large indexing job into many small tasks and submit using SLURM

# ./turbo-index my-files.lst label my.geom /location/for/streams

SPLIT=20000  # Size of job chunks

INPUT=/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/data_processing/proc_processing/Euxfel/r0108/files.lst
RUN=$(sed 's/.lst//g'<<<$(basename $INPUT))

GEOM=/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/data_processing/proc_processing/Euxfel/agipd_2450_v9_wo_mask_vds.geom
PDB=/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/1VDS.cell 


STREAMDIR=/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/data_processing/proc_processing/Euxfel/r0108/streams
SAVEPATH=/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/data_processing/proc_processing/Euxfel/r0108/lists
ERRORDIR=/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/data_processing/proc_processing/Euxfel/r0108/error

source /etc/profile.d/modules.sh
module load xray
#module load crystfel
module load hdf5/1.10.5

for FILE1 in `cat $INPUT`; do
    RUN=$(sed 's/.cxi//g'<<<$(basename $FILE1))
    echo $FILE1 > $SAVEPATH/tmp.lst
    /home/galchenm/work_scripts/build/list_events -i $SAVEPATH/tmp.lst -g $GEOM -o $SAVEPATH/events-${RUN}.lst
    split -a 3 -d -l $SPLIT $SAVEPATH/events-${RUN}.lst $SAVEPATH/split-events-${RUN}.lst
    rm -f $SAVEPATH/events-${RUN}.lst
    rm -f $SAVEPATH/tmp.lst

# Set up environment here if necessary
#source /path/to/crystfel/setup.sh

# If you are using single-event files instead of multi-event ("CXI") ones,
# comment out the above lines and uncomment the following one:
#cp $INPUT events-${RUN}.lst
#echo "Total number\n"
# Count total number of events
#wc -l events-${RUN}.lst

echo "Start Sbatch"
# Loop over the event list files, and submit a batch job for each of them
for FILE in $SAVEPATH/split-events-${RUN}.lst*; do

    # Stream file is the output of crystfel
    STREAM=`echo $FILE | sed -e "s/split-events-${RUN}.lst/${RUN}.stream/"`
    STREAM=$STREAMDIR/$(basename $STREAM)
    # Job name
    NAME=`echo $FILE | sed -e "s/split-events-${RUN}.lst/${RUN}-/"`
    NAMEOUT=$(basename $NAME)
    # Job number
    NUMBER=${NAME##$RUN-}
    Q=`echo $NUMBER |grep -Eo '[0-9]+$'`
    #echo $Q
    POS=`expr $Q \* $SPLIT + 1`
    #echo $POS

    echo "$NAME (serial start $POS): $FILE  --->  $STREAM"

    SLURMFILE="${NAME}.sh"

    echo "#!/bin/sh" > $SLURMFILE
    echo >> $SLURMFILE

    echo "#SBATCH --partition=upex" >> $SLURMFILE  # Set your partition here

    echo "#SBATCH --time=24:00:00" >> $SLURMFILE
    echo "#SBATCH --exclude=max-exfl036,max-exfl084" >> $SLURMFILE
    echo "#SBATCH --nodes=1" >> $SLURMFILE
    echo "#SBATCH --nice=10" >> $SLURMFILE
#    echo "#SBATCH --mem=500000" >> $SLURMFILE
    echo >> $SLURMFILE

    echo "#SBATCH --job-name  $STREAM" >> $SLURMFILE
    echo "#SBATCH --output    $ERRORDIR/$NAMEOUT-%N-%j.out" >> $SLURMFILE
    echo "#SBATCH --error     $ERRORDIR/$NAMEOUT-%N-%j.err" >> $SLURMFILE
    echo >> $SLURMFILE

    echo "source /etc/profile.d/modules.sh" >> $SLURMFILE
    echo "module load xray" >> $SLURMFILE


    echo >> $SLURMFILE

    command="/home/galchenm/work_scripts/new_cryst_xgand/crystfel-0.9.1/crystfel/build/indexamajig -i $FILE -o $STREAM --serial-start=$POS"

    command="$command -j 80 -g $GEOM"

    #command="$command --peaks=peakfinder8 --min-snr=6 --threshold=300 --min-pix-count=1 --max-pix-count=30 --min-res=30 --max-res=400 --min-peaks=20"
    command="$command --peaks=peakfinder8 --min-snr=8 --threshold=120 --min-pix-count=1 --max-pix-count=30 --min-res=20 --int-radius=2,4,7 --min-peaks=20"

    command="$command --copy-hdf5=/entry_1/pulseId"
    command="$command --copy-hdf5=/entry_1/trainId"
    command="$command --copy-hdf5=/entry_1/cellId"

    #command="$command -p $PDB --indexing=xgandalf --no-check-peaks --no-revalidate"
    command="$command -p $PDB --indexing=none --no-check-peaks --no-revalidate"

    echo $command >> $SLURMFILE

    sbatch $SLURMFILE

  done

done

