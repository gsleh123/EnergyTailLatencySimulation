#!/bin/bash -l
#
#SBATCH --job-name=test
#SBATCH --output=res.txt
#
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem 4000
#SBATCH --mail-user=gleh@ucdavis.edu
#SBATCH --mail-type=ALL

#. ~/.bashrc
#cd CoreClockSimulator/coreclock-simulator/
#source activate py2_ghosal
srun ./runTheoreticalSim.sh
#source deactivate py2_ghosal
