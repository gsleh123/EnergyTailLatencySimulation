#!/bin/bash

rm *.csv

. ~/.bashrc
source activate py2_ghosal
python simulation.py
echo Done
