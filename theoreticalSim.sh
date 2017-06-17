#!/bin/bash

rm *.csv

arrival_kwargs=arrival_kwargs
arg1="'scale'"
arg2=1

arr_rate[0]=1
arr_rate[1]=0.333333
arr_rate[2]=0.2
arr_rate[3]=0.142857
arr_rate[4]=0.111111
arr_rate[5]=0.090909
arr_rate[6]=0.076923
arr_rate[7]=0.066667
arr_rate[8]=0.058824
arr_rate[9]=0.052632
arr_rate[10]=0.047619
arr_rate[11]=0.043478
arr_rate[12]=0.04
arr_rate[13]=0.037037
arr_rate[14]=0.034483
arr_rate[15]=0.032258
arr_rate[16]=0.030303
arr_rate[17]=0.028571
arr_rate[18]=0.027027
arr_rate[19]=0.025641
arr_rate[20]=0.02439
arr_rate[21]=0.023256
arr_rate[22]=0.022222
arr_rate[23]=0.021277
arr_rate[24]=0.020408
arr_rate[25]=0.019608
arr_rate[26]=0.018868
arr_rate[27]=0.018182
arr_rate[28]=0.017544
arr_rate[29]=0.016949
arr_rate[30]=0.016393
arr_rate[31]=0.015873
arr_rate[32]=0.015385
arr_rate[33]=0.014925
arr_rate[34]=0.014493
arr_rate[35]=0.014085
arr_rate[36]=0.013699
arr_rate[37]=0.013333
arr_rate[38]=0.012987
arr_rate[39]=0.012658

. ~/.bashrc
source activate py2_ghosal
python CCRunner.py Energy.ini
echo Done

for run in {1..39}
do
arg2=${arr_rate[$run - 1]}
textToSearch="$arrival_kwargs"' = {'"$arg1"': '"$arg2}"
arg2=${arr_rate[$run]}
textToReplace="$arrival_kwargs"' = {'"$arg1"': '"$arg2}"
python editFile.py "$textToSearch" "$textToReplace"
python CCRunner.py Energy.ini
echo Done
done

arg2=${arr_rate[39]}
textToSearch="$arrival_kwargs"' = {'"$arg1"': '"$arg2}"
arg2=${arr_rate[0]}
textToReplace="$arrival_kwargs"' = {'"$arg1"': '"$arg2}"
python editFile.py "$textToSearch" "$textToReplace"

