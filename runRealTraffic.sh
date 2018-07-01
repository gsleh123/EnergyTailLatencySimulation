#!/bin/bash -l
#
#SBATCH --job-name=realTraffic
#SBATCH --output=realTraffic.txt
#
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem 2000

srun ./realTraffic.sh
