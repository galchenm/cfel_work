#!/bin/bash

#grep the Beamtime_ID and save it to the variable i
i=`ls /gpfs/current/*eamt* | grep -o '[0-9]\+'` 2>/dev/null

#define the date as YYYYMMDD 
d=`date +"%Y%m%d"`




if [ "$i" -ge "0" ] 2>/dev/null

 then 
  echo 
  echo The Beamtime ID of this session is ${i}
  echo 
  echo "CrystalControl log file will be saved under the name" CC_${d}_${i}.log
  echo 
  echo  " " >> /gpfs/local/shared/CrystalControlEiger/log/CC_${d}_${i}.log
  echo "Starting Logging CrystalControl with Beamtime ID: ${i}" >> /gpfs/local/shared/CrystalControlEiger/log/CC_${d}_${i}.log
  echo  " " >> /gpfs/local/shared/CrystalControlEiger/log/CC_${d}_${i}.log


###############
# start crystalcontrol 
# 2>&1 redirect the output to the | command
# append each line of the output with the date and send it to the | command
# save the file as /gpfs/local/shared/Crystalcontrol/CC_DATE_BeamtimeID.log
###############

#python -u /gpfs/local/shared/CrystalControl/crystalControl.py 2>&1 | while read line; do echo `date +"%A %d-%m-%Y  %T  (KW %V) "` ":" $line; done | tee -a /gpfs/local/shared/CrystalControl/CC_Log/CC_${d}_${i}.log
python3 -u /gpfs/local/shared/CrystalControlEiger/crystalControl.py 2>&1 | while read line; do echo `date +"%A %d-%m-%Y  %T  (KW %V) "` ":" $line; done | tee -a /gpfs/local/shared/CrystalControlEiger/log/CC_${d}_${i}.log


 else 

  echo 
  echo "No Beamtime_ID found!!!!"
  echo 
  echo "CrystalControl log file will be saved under the name" CC_${d}_local.log   
  echo 
  echo  >> /gpfs/local/shared/CrystalControlEiger/log/CC_${d}_local.log
  echo "Starting Logging CrystalControl with Beamtime ID: local" >> /gpfs/local/shared/CrystalControlEiger/log/CC_${d}_local.log
  echo  >> /gpfs/local/shared/CrystalControlEiger/log/CC_${d}_local.log


#python -u /gpfs/local/shared/CrystalControl/crystalControl.py 2>&1 | while read line; do echo `date +"%A %d-%m-%Y  %T  (KW %V) "` ":" $line; done | tee -a /gpfs/local/shared/CrystalControl/CC_Log/CC_${d}_local.log
python3 -u /gpfs/local/shared/CrystalControlEiger/crystalControl.py 2>&1 | while read line; do echo `date +"%A %d-%m-%Y  %T  (KW %V) "` ":" $line; done | tee -a /gpfs/local/shared/CrystalControlEiger/log/CC_${d}_${i}.log


fi

#BKP
#  python -u /gpfs/local/shared/CrystalControl/crystalControl.py 2>&1 | while read line; do echo $(date) ":" $line; done | tee -a  /gpfs/local/shared/CrystalControl/CC_${d}_local.log
