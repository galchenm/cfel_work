#!/bin/bash

# Split a large indexing job into many small tasks and submit using SLURM

# ./turbo-index my-files.lst label my.geom /location/for/streams

# Copyright © 2016-2017 Deutsches Elektronen-Synchrotron DESY,
#                       a research centre of the Helmholtz Association.
#
# Authors:
#   2016      Steve Aplin <steve.aplin@desy.de>
#   2016-2017 Thomas White <taw@physics.org>

SPLIT=140000  # Size of job chunks
INPUT=/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/data_processing/cheetah_processing/updating/files.lst
RUN=$(sed 's/.lst//g'<<<$(basename $INPUT))
GEOM=/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/agipd_2450_v4.geom 
PDB=/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/1VDS.cell 


STREAMDIR=/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/data_processing/cheetah_processing/updating/streams
OUTPATH=/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/data_processing/cheetah_processing/updating/out
SAVEPATH=/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/data_processing/cheetah_processing/updating/lists
ERRORDIR=/gpfs/cfel/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/data_processing/cheetah_processing/updating/error

source /etc/profile.d/modules.sh
module load xray
module load crystfel

for FILE1 in `cat $INPUT`; do
    #echo $FILE1
    #echo $(basename $FILE1)
    #echo $(sed 's/.cxi//g'<<<$(basename $FILE1))
    RUN=$(sed 's/.cxi//g'<<<$(basename $FILE1))
    #echo $RUN
    #RUN="${RUN:9:10}"
    #echo $RUN
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

# Count total number of events
#wc -l events-${RUN}.lst

# Loop over the event list files, and submit a batch job for each of them
for FILE in $SAVEPATH/split-events-${RUN}.lst*; do

    # Stream file is the output of crystfel
    STREAM=`echo $FILE | sed -e "s/split-events-${RUN}.lst/${RUN}.stream/"`
    #echo $STREAM
    STREAM=$STREAMDIR/$(basename $STREAM)
    # Job name
    NAME=`echo $FILE | sed -e "s/split-events-${RUN}.lst/${RUN}-/"`
    NAMEOUT=$(basename $NAME)
    # Job number
    NUMBER=${NAME##$RUN-}
    #echo $NUMBER
    #echo $NUMBER |grep -Eo '[0-9]+$'
    Q=`echo $NUMBER |grep -Eo '[0-9]+$'`
    #echo $Q
    POS=`expr $Q \* $SPLIT + 1`
    #echo $POS

    echo "$NAME (serial start $POS): $FILE  --->  $STREAM"

    SLURMFILE="${NAME}.sh"

    echo "#!/bin/sh" > $SLURMFILE
    echo >> $SLURMFILE

    echo "#SBATCH --partition=upex" >> $SLURMFILE  # Set your partition here
#    echo "#SBATCH --partition=all" >> $SLURMFILE  # Set your partition here
    echo "#SBATCH --time=24:00:00" >> $SLURMFILE
#    echo "#SBATCH --exclude=max-exfl094,max-exfl095,max-exfl096,max-exfl049,max-exfl047,max-exfl048,max-exfl024,max-exfl036,max-exfl037,max-exfl022,max-exfl082,max-exfl085,max-exfl142,max-exfl200" >> $SLURMFILE
#    echo "#SBATCH --exclude=max-exfl109,max-exfl103" >> $SLURMFILE
    echo "#SBATCH --nodes=1" >> $SLURMFILE
    echo "#SBATCH --nice=10" >> $SLURMFILE
#    echo "#SBATCH --mem=500000" >> $SLURMFILE
    echo >> $SLURMFILE

#    echo "#SBATCH --workdir   $PWD" >> $SLURMFILE
    echo "#SBATCH --job-name  $STREAM" >> $SLURMFILE
    #echo "#SBATCH --output    $NAME-%N-%j.out" >> $SLURMFILE
    #echo "#SBATCH --error     $NAME-%N-%j.err" >> $SLURMFILE
    echo "#SBATCH --output    $ERRORDIR/$NAMEOUT-%N-%j.out" >> $SLURMFILE
    echo "#SBATCH --error     $ERRORDIR/$NAMEOUT-%N-%j.err" >> $SLURMFILE
    echo >> $SLURMFILE

    echo "source /etc/profile.d/modules.sh" >> $SLURMFILE
    echo "module load xray" >> $SLURMFILE
    echo "module load crystfel" >> $SLURMFILE
#    echo "source /gpfs/cfel/cxi/common/public/cfelsoft-rh7-public/conda-setup.sh" >> $SLURMFILE
#    echo "conda activate cfel_crystallography" >> $SLURMFILE
    echo >> $SLURMFILE

    command="indexamajig -i $FILE -o $STREAM --serial-start=$POS"
#old
    command="$command -j 80 -g $GEOM"
#next    command="$command -j 80 -g $GEOM -p $PDB --int-radius=2,3,4"
    command="$command --peaks=peakfinder8 --min-snr=6 --threshold=300 --min-pix-count=1 --max-pix-count=30 --min-res=30 --max-res=700 --min-peaks=30"
#-    command="$command --peaks=cxi --hdf5-peaks=/data/peaks"
#old    command="$command --indexing=mosflm-latt-nocell --no-check-cell --no-cell-combinations --no-multi --no-retry"
#    command="$command --indexing=xgandalf --no-cell-combinations --nomulti"
#-    command="$command --copy-hdf5=/instrument/photon_energy_eV --copy-hdf5=/instrument/detector_1/EncoderValue --copy-hdf5=/entry_1/experiment_identifier"
#    command="$command --copy-hdf5=/instrument/photon_energy_eV --copy-hdf5=/instrument/detector_1/EncoderValue"
command="$command --copy-hdf5=/instrument/pulseID"
    command="$command --copy-hdf5=/instrument/trainID"
    command="$command --copy-hdf5=/instrument/cellID"
     command="$command -p $PDB --indexing=mosflm-latt-nocell --no-check-cell"
     #command="$command -p $PDB --indexing=mosflm-latt-nocell"

    #command="$command --peaks=zaef"  # Indexing parameters here

    echo $command >> $SLURMFILE

    sbatch $SLURMFILE

  done

done

