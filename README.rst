EnergyTailLatency Simulator
===================

The EnergyTailLatency Simulator is a python-based simulation of to determine the tail latency and energy consumption of a given system. As of now, the code above only uses 1 Distribution Server and N Leaf Servers, but this can easily be tweaked. The Distribution Server distributes the packets to the Leaf Servers.

Running CoreClock Simulator
---------------------------

A anaconda environment "py_conda_env.yml" is provided to create the required environment. `Download Miniconda <http://conda.pydata.org/miniconda.html>`_ Miniconda2 vs Miniconda3 doesn't really matter. To recreate the environment, open a terminal and run "conda env create -f environment.yml". 

Note: The current yml file may not necessarily contain all the packages needed to run the simulation. On Windows, uncomment the lines that were commented. These packages were Windows Dependent. On Linux, use the current yml file and add packages as needed. 

Running the code
----------------
To Run: Run CCRunner.py needs to have at least one argument and that is the configuration file. For this specific code, we are using Energy.ini as the configuration file. The ini file contains all the configurations for the simulation. The second argument is optional and is used to pass in the traffic trace for real traffic.

For all configurations, make sure the interpreter is pointing to the conda-created environment (Something like C:\Miniconda2\envs\py2_ghosal\python.exe for windows)

1) CCRunner configuration with only the ini file

Script: CCRunner.py
Script parameters: Energy.ini
Full Command: python CCRunner.py Energy.ini 

2) CCRunner configuration with ini file and real traffic trace

Script: CCRunner.py
Script parameters: Energy.ini someFile.txt
Full Command: python CCRunner.py Energy.ini someFile.txt

someFile.txt contains all the inter arrival times of the real traffic. The format of the text file should be one inter arrival time per line. 

All settings should be changed in Energy.ini. A description of these settings can be found below. 

When running to verify the theoretical results, there is a script available that will automatically change the arrival rate called theoreticalSim.sh and runTheoreticalSim.sh. 

In order to run multiple simulations with different settings without having to manually run them, it's possible to use bash scripts to start the next simulation. For example, thereoticalSim.sh has all the different inter-arrival times and uses the python file editFile.py to change the arrival rates found in Energy.ini. For systems that use SLURM Workload Manager like the UC Davis College of Engineering HPC, we have to specify the duration of the job as well as the memory limit. This is done in runTheoreticalSim.sh. Otherwise, on any other machine, we simply excecute theoreticalSim.sh. 

Simulation Overview
-------------------

The overall simulation works using Simpy, a python library for simulation. The only thing that really matters is the simpy environment (stored in simenv.py). The simulation is asynchronous (each host runs its own "threads" -- one for arrivals and one for computation). They aren't really threads, but simpy makes the programming feel that way. env.timeout will sleep a thread for a given amount of time--this is how we simulation computation, packet arrival, etc. For example, if a host is "generating" data, it will predetermine the time until the next packet arrival through sampling a distribution, and the sleep (using env.timeout) for that long. Simpy will automatically wake up the "thread" and continue where it left off. This is why you will see a lot of functions surrounded by "while True:". Think of each of these functions as an async "thread".

There are a few files that make up the core of the simulation.

CCRunner.py
^^^^^^^^^^^

The starting point of the program. It calls CCSimulator.py.

CCSimulator.py
^^^^^^^^^^^^^^

run(): runs the simulation, and create the csv file. 


CreateConfigDict.py
^^^^^^^^^^^^^^^^^^^

create_config_dict(): It's a huge function, but very simple. The parser given is a ConfigParser.SafeConfigParser() that can read the ini file. This function just converts all the ini data into a configuration dictionary that is passed around to everything for simulation setup. There are also some hard-coded default values in case the ini file doesn't have them. Some of these settings may be used or not.

Host.py
^^^^^^^
init_hosts(config): All it does is create the servers that we need for the simulation given the settings from the config dictionary. 

get_hosts(): Returns the host list 

DistributionHost.py
^^^^^^^^^^^^^^^^^^^

The DistributionHost is responsible for creating and sending packets to the ProcessHost.  
    process_arrivals_ipp(self): This function generates the packets using the IPP (interrupted Poisson Process). The IPP is simply a model with two states where one state generates packets really quickly and the other state the packets generate slowly depending on some alpha and beta values. This is how we can create bursty traffic. After generating the packet, the distribution server randomly chooses which process server it should send the packet. 
    process_arrivals_ipp_mode(self): This function allows the IPP to switch between the on and off state. 
    process_arrivals_real(self): This function uses the data from a real traffic trace to generate packets.
    process_arrivals_theoretical(self): This function generates data from the specific distribution that we are considering. Usually, this is Poisson.
    create_packet(self, env): Simply create a new packet and distribute it to a server. 
    
EnergyRunner.py
^^^^^^^^^^^^^^^

Energy_Runner(target_timestep): Runs the simulation and is responsible for stopping it once we hit the time limit. 

ProcessHost.py
^^^^^^^^^^^^^^

    ProcessHost: The ProcessHost is responsible for processing the packets. 
      process_service(self): It'll either process the packet, go to sleep, or do nothing. 
      wake_up_server(self, env): Set the server state to booting.
      finish_booting_server(self, env, time_to_wake_up): Set server state to awake.
      sleep_server(self, env): Set server state to sleep. 
      end_sim(self, env): Ends the simulation by putting all the servers to sleep so that we can properly calculate the power and tail latency in Vis_Energy. 
      
PoissonAlgorithm.py
^^^^^^^^^^^^^^^^^^^

find_hosts(): This is the Poisson algorithm to find the theoretical number of servers and frequency. 

Vis_Energy.py
^^^^^^^^^^^^^

This outputs a csv file with raw data. The csv file is then processed in MATLAB. The MATLAB programs can be found in CreateGraphs Folder. 

editFile.py
^^^^^^^^^^^

This file goes into Energy.ini and finds a text to replace with something else. 

Energy.ini
^^^^^^^^^^

The following configurations are listed under CC_Config. 

timesteps
  This determines how long the simulation should run. In this particular simulation, the units are in milliseconds, so 300,000 is 5     minutes.

mpip_report_type
  Leave it at Energy.
  
req_size
  This was agreed upon to be 1,000,000 bytes or 1MB. 

timescale
  This is the timescale the simulation runs at. 1000 means it runs at ms. 
  
random_seed
 This is just choosing which seed to pick for the random variables. This way we can reproduce the results. 
 
The following configurations are listed under Energy. 

sim_mode
  There's an option between Theoretical, IPP, or Real Traffic. 
  
d_0
  Tail latency constraint. 0.01 means that packets need to be processed before 0.01s or 10ms. 

P_s
  This is the power consumption during sleep and booting stages. This is 50W. 

alpha
  Some factor for the theoretical algorithm. It's 1000 right now. 

num_of_servers
  Control the total amount of servers available to the simulation. 

e
  This determines how many packets can go over d_0. Thus, a value of 0.1 means, only 10% of the packet will be over 10ms. 

s_b 
  Base frequency - 1.2

s_c
  Max frequency - 3

pow_con_model
  This can either be 1 or 2 depending on the mode. 

k_m
  This is the power coefficient and depends on the power conservation model. 

b
  This is some offset for the power when calculating the power usage.
 
alphaThresh
  Setting for burst level ranging from 0 to 1. alphaThresh + betaThresh must always equal 1. Higher alphaThresh values correspond to less bursts of traffic. Thus, an alphaThresh of 1 leads to the normal Poisson Process. alphaThresh can also never be 0. 
  
betaThresh
  Setting for burst level ranging from 0 to 1. alphaThresh + betaThresh must always equal 1. Higher betaThresh values correspond to more bursts of traffic.

active_servers
  How many servers to be used to process packets. 
  
servers_to_use
 This is the max number of servers the system can use. 
 
freq_to_use
  This is used for problem_type 4 and allows us to fix the frequency to our chosen value. This comes in helpful when we are trying to figure out the frequency to use to meet the tail latency when dealing with different bursts of traffic. 
  
The problem_type and freq_setting is only useful for running the theoretical simulation to verify the results. Almost all other cases where we are going to extend the theoretical model will involve using optimal number of servers and optimal frequency, so we should just leave the problem_type and freq_setting to 1. 

routing_option
  Choose how to distribute the packets. There's minimum queue length where the packet is sent to the server with the least packets and there's a random distribution. 
  
dvfs_option
  Choose between the modified Rubik's algorithm or not using DVFS. 
  
  The modified Rubik's algorithm is basically looking at every packet in the queue and looking at the time left before the packet violates the time guarantee. Then we calculate the frequency from this time remaining. 
  
problem_type
  1: Optimal Number of Servers
  2: Min Number of Servers
  3: Max Number of Servers
  4: Custom number of servers and custom frequency
  
freq_setting
  1: Optimal Frequency
  2: Max Frequency

wake_up_distribution
  The distribution for waking up a server. 

wake_up_kwargs
  The time to wake up a server.
  
arrival_distribution
  The distribution for the next packet. 
  
arrival_kwargs
  The interarrival times of the packets. This is the inverse of the arrival rate.

packet_window_size
  Look at the last packet window size to determine whether to add servers or not. 
  
CSV Format
^^^^^^^^^^

Base Naming Convention - This is the naming convention given by the simulation. 

simdata[problem_type][freq_setting]N=[num_of_servers]k=[power_setting].csv

For example, simdata32N=32k=2.csv will have a problem_type of 3 (max servers used), freq setting of 2(max frequency), 32 total servers, and using the second power model. You will want to rename the csv files to add in more descriptions of the simulation run. 

The columns of the csv will follow the format shown below. Each row will just be a new simulation run since the code appends to the csv.
Format: Arrival Rate (req/s), Inter-arrival times (s/req), Servers used, Freq (GHz), Computation Rate (%), Waking Up Rate (%), Sleep Rate (%), Tail Latency (%), Total Power Usage (W)
