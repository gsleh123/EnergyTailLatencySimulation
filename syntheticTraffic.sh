#!/bin/bash

rm *.csv

alpha_thresh=alphaThresh
beta_thresh=betaThresh
arg2=0.1

beta[0]=0.1
beta[1]=0.25
beta[2]=0.5
beta[3]=0.75
beta[4]=1
beta[5]=25
beta[6]=50
beta[7]=75
beta[8]=100
beta[9]=250

. ~/.bashrc
source activate py2_ghosal
python CCRunner.py Energy.ini
echo Done

for run in {1..9}
do
arg2=${beta[$run - 1]}
textToSearch="$beta_thresh"' = '"$arg2"
arg2=${beta[$run]}
textToReplace="$beta_thresh"' = '"$arg2"
python editFile.py "$textToSearch" "$textToReplace"

arg2=${beta[$run - 1]}
textToSearch="$alpha_thresh"' = '"$arg2"
arg2=${beta[$run]}
textToReplace="$alpha_thresh"' = '"$arg2"
python editFile.py "$textToSearch" "$textToReplace"

python CCRunner.py Energy.ini
echo Done
echo $textToSearch
echo $textToReplace
done

arg2=${beta[9]}
textToSearch="$beta_thresh"' = '"$arg2"
arg2=${beta[0]}
textToReplace="$beta_thresh"' = '"$arg2"
python editFile.py "$textToSearch" "$textToReplace"

arg2=${beta[9]}
textToSearch="$alpha_thresh"' = '"$arg2"
arg2=${beta[0]}
textToReplace="$alpha_thresh"' = '"$arg2"
python editFile.py "$textToSearch" "$textToReplace"

