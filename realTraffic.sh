#!/bin/bash

rm *.csv

. ~/.bashrc
source activate py2_ghosal
python CCRunner.py Energy.ini high_rate_iatimes_400.txt
echo Done
