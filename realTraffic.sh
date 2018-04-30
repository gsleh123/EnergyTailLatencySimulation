#!/bin/bash

rm *.csv

. ~/.bashrc
source activate py2_ghosal
python CCRunner.py Energy.ini low_rate_iatimes_100.txt
echo Done
