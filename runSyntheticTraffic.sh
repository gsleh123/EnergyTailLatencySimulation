#!/bin/bash -l
#
#SBATCH --job-name=synthetic_traffic
#SBATCH --output=synthetic_traffic.txt
#
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem 2000
#SBATCH --mail-user=gleh@ucdavis.edu
#SBATCH --mail-type=ALL

srun ./syntheticTraffic.sh
