#!/bin/bash

rm *.csv

alpha_thresh=alphaThresh
beta_thresh=betaThresh
arg2=0.01

beta_thresh[0]=0.01
beta_thresh[1]=0.1
beta_thresh[2]=1
beta_thresh[3]=10
beta_thresh[4]=100

. ~/.bashrc
source activate py2_ghosal
python CCRunner.py Energy.ini
echo Done

for run in {1..4}
do
arg2=${beta_thresh[$run - 1]}
textToSearch="$beta_thresh"' = '"$arg2"
arg2=${beta_thresh[$run]}
textToReplace="$beta_thresh"' = '"$arg2"
python editFile.py "$textToSearch" "$textToReplace"

arg2=${beta_thresh[$run - 1]}
textToSearch="$beta_thresh"' = '"$arg2"
arg2=${beta_thresh[$run]}
textToReplace="$alpha_thresh"' = '"$arg2"
python editFile.py "$textToSearch" "$textToReplace"

python CCRunner.py Energy.ini
echo Done
done

arg2=${beta_thresh[4]}
textToSearch="$beta_thresh"' = '"$arg2"
arg2=${beta_thresh[0]}
textToReplace="$beta_thresh"' = '"$arg2"
python editFile.py "$textToSearch" "$textToReplace"

arg2=${beta_thresh[4]}
textToSearch="$alpha_thresh"' = '"$arg2"
arg2=${beta_thresh[0]}
textToReplace="$alpha_thresh"' = '"$arg2"
python editFile.py "$textToSearch" "$textToReplace"

