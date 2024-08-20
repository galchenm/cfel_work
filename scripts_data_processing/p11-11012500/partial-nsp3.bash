#!/bin/bash

INPUT=$1
stream=$(sed 's/.stream//g'<<<$(basename $INPUT))
#09 data=${stream}_part09_maxadu_push1
data=amb-${stream}_xsphere
pg="4/mmm" #-3m1_H  #4/mmm #symmetry, like 422 or 4/mmm
pdb="/asap3/petra3/gpfs/p11/2021/data/11010507/scratch_cc/galchenm/pdb/nsp3-hex.cell"

HIGHRES=2.45
resext=0.0 # total CC* is calculated to highres+resext
highres="--highres=${HIGHRES}"      #<- number gives res limit
nsh=20 # number of shells
#maxB="--max-rel-B=50"
model=xsphere
#model=unity
iterations=3 #2,3
push="--push-res=1.0" #"--push-res=0.2" "--push-res=0.5" "--push-res=1.5"
minres="--min-res=5"

PGY1="-3m1_H"
PGW1="6/mmm"
PGY2="-3_H"
PGW2="-3m1_H"


partialator="partialator"
ambigator="ambigator"

ERRORDIR=error

source /etc/profile.d/modules.sh
module load xray
module load hdf5/1.10.5
    # Job name
    NAME=$data

    SLURMFILE="${NAME}.sh"

    echo "#!/bin/sh" > $SLURMFILE
    echo >> $SLURMFILE

#    echo "#SBATCH --partition=cfel" >> $SLURMFILE  # Set your partition here
    echo "#SBATCH --partition=upex" >> $SLURMFILE  # Set your partition here
#    echo "#SBATCH --partition=all" >> $SLURMFILE  # Set your partition here
    echo "#SBATCH --time=240:00:00" >> $SLURMFILE
#    echo "#SBATCH --exclude=max-exfl109,max-exfl103" >> $SLURMFILE
    echo "#SBATCH --nodes=1" >> $SLURMFILE
    echo "#SBATCH --nice=100" >> $SLURMFILE
    echo "#SBATCH --mem=500000" >> $SLURMFILE
    echo "#SBATCH --cpu-freq=2600000" >> $SLURMFILE  # TO TEST !!!
    echo >> $SLURMFILE

#    echo "#SBATCH --workdir   $PWD" >> $SLURMFILE
    echo "#SBATCH --job-name  $NAME" >> $SLURMFILE
    echo "#SBATCH --output    $ERRORDIR/$NAME-%N-%j.out" >> $SLURMFILE
    echo "#SBATCH --error     $ERRORDIR/$NAME-%N-%j.err" >> $SLURMFILE
    echo >> $SLURMFILE

    echo "source /etc/profile.d/modules.sh" >> $SLURMFILE
    echo "module load xray" >> $SLURMFILE
    echo "module load hdf5/1.10.5">> $SLURMFILE
	echo "module load anaconda3/5.2">> $SLURMFILE
	echo "module load crystfel">> $SLURMFILE
	echo "export QT_QPA_PLATFORM=offscreen" >> $SLURMFILE 
    #echo "export PATH=/home/galchenm/huina:$PATH" >> $SLURMFILE
    echo >> $SLURMFILE




command="$ambigator $stream.stream -y ${PGY1} -w ${PGW1} --ncorr=15000 -n 50 -j 128 --fg-graph=fg_6m1.dat -o amb-$stream-temp1.stream #--lowres=20 --highres=2 "
#echo $command >> $SLURMFILE                         
command="$ambigator amb-$stream-temp1.stream  -y ${PGY2} -w ${PGW2} --ncorr=15000 -n 50 -j 128 --fg-graph=fg_6m2.dat -o amb-$stream-temp2.stream #--lowres=20 --highres=2"

#echo $command >> $SLURMFILE


    #command="$partialator --no-logs --max-adu=7500 --iterations=$iterations --model=$model "$maxB" "$minres" "$push" -i $stream.stream -o $data.hkl -y $pg -j 80"
    #command="$partialator --no-logs --max-adu=7500 --iterations=$iterations --model=$model "$maxB" "$minres" "$push" -i $stream.stream -o $data.hkl -y $pg -j 80"
    command="$partialator --no-logs --iterations=$iterations --model=$model "$minres" "$push" -i amb-$stream-temp2.stream  -o $data.hkl -y ${PGY2} -j 80"
    #echo $command >> $SLURMFILE
        #total CC* calculation
    highres1="--highres="`echo $HIGHRES + $resext | bc`
#    echo $highres1
    command="compare_hkl -p $pdb -y ${PGY2} $highres1 --nshells=1 --fom=CCstar --shell-file=${data}_CCstarTotal.dat $data.hkl1 $data.hkl2"
    echo $command >> $SLURMFILE

    command="compare_hkl -p $pdb -y ${PGY2} $highres --nshells=$nsh --fom=CCstar --shell-file=${data}_CCstar.dat $data.hkl1 $data.hkl2"
    echo $command >> $SLURMFILE

    command="compare_hkl -p $pdb -y ${PGY2} "$highres" --nshells=$nsh --fom=Rsplit --shell-file=${data}_Rsplit.dat $data.hkl1 $data.hkl2"
    echo $command >> $SLURMFILE

    command="compare_hkl -p $pdb -y ${PGY2} "$highres" --nshells=$nsh --fom=CC --shell-file=${data}_CC.dat $data.hkl1 $data.hkl2"
    echo $command >> $SLURMFILE

    command="compare_hkl -p $pdb -y ${PGY2} "$highres" --nshells=$nsh --fom=CCano --shell-file=${data}_CCano.dat $data.hkl1 $data.hkl2"
    echo $command >> $SLURMFILE

    command="check_hkl -p $pdb -y ${PGY2} "$highres" --nshells=$nsh --shell-file=${data}_SNR.dat $data.hkl"
    echo $command >> $SLURMFILE

    command="check_hkl -p $pdb -y ${PGY2} "$highres" --nshells=$nsh --wilson --shell-file=${data}_Wilson.dat $data.hkl"
    echo $command >> $SLURMFILE
	max_dd=$(echo "scale=3;10./${HIGHRES}" | bc)

	command="python3 /gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/plot_func/many_plots-upt-v2.py -i ${data}_CCstar.dat -x '1/d' -y 'CC*' -o ${data}.png -add_nargs ${data}_Rsplit.dat -yad 'Rsplit/%' -x_lim_dw 1. -x_lim_up ${max_dd} -t ${data} -legend ${data} >> $ERRORDIR/output.err"
	echo $command >> $SLURMFILE
    sbatch $SLURMFILE

