#!/bin/bash

rm *.csv

alpha_thresh=alphaThresh
beta_thresh=betaThresh
arg2=0.01

beta[0]=0.05
beta[1]=0.1
beta[2]=0.15
beta[3]=0.2
beta[4]=0.25
beta[5]=0.3
beta[6]=0.35
beta[7]=0.4
beta[8]=0.45
beta[9]=0.5
beta[10]=0.55
beta[11]=0.6
beta[12]=0.65
beta[13]=0.7
beta[14]=0.75
beta[15]=0.8
beta[16]=0.85
beta[17]=0.9
beta[18]=0.95

. ~/.bashrc
source activate py2_ghosal
python CCRunner.py Energy.ini
echo Done

for run in {1..18}
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

arg2=${beta[18]}
textToSearch="$beta_thresh"' = '"$arg2"
arg2=${beta[0]}
textToReplace="$beta_thresh"' = '"$arg2"
python editFile.py "$textToSearch" "$textToReplace"

arg2=${beta[18]}
textToSearch="$alpha_thresh"' = '"$arg2"
arg2=${beta[0]}
textToReplace="$alpha_thresh"' = '"$arg2"
python editFile.py "$textToSearch" "$textToReplace"

