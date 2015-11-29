
from Simulator import Simulator

RANDOM_SEED = 29
SIM_TIME = 100000
MU = 1

def main():
	simulator = Simulator(RANDOM_SEED, SIM_TIME)
	simulator.Run(MU)

if __name__ == '__main__':
	main()
