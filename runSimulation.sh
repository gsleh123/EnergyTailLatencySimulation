#!/bin/bash -l
#
#SBATCH --job-name=simulation
#SBATCH --output=simulation.txt
#
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem 2000

srun ./simulation.sh
