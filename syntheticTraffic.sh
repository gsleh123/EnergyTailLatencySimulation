#!/bin/bash

rm *.csv

alpha_thresh=alphaThresh
beta_thresh=betaThresh
arg2=0.0001

beta[0]=0.001
beta[1]=0.0025
beta[2]=0.005
beta[3]=0.0075
beta[4]=0.01
beta[5]=0.025
beta[6]=0.05
beta[7]=0.075
beta[8]=0.1

. ~/.bashrc
source activate py2_ghosal
python CCRunner.py Energy.ini
echo Done

for run in {1..8}
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

arg2=${beta[8]}
textToSearch="$beta_thresh"' = '"$arg2"
arg2=${beta[0]}
textToReplace="$beta_thresh"' = '"$arg2"
python editFile.py "$textToSearch" "$textToReplace"

arg2=${beta[8]}
textToSearch="$alpha_thresh"' = '"$arg2"
arg2=${beta[0]}
textToReplace="$alpha_thresh"' = '"$arg2"
python editFile.py "$textToSearch" "$textToReplace"

