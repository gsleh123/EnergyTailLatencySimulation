#!/bin/bash -l
#
#SBATCH --job-name=theoretical_sim
#SBATCH --output=theoretical_sim.txt
#
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem 2000

srun ./theoreticalSim.sh
