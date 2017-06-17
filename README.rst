EnergyTailLatency Simulator
===================

The EnergyTailLatency Simulator is a python-based simulation of to determine the tail latency and energy consumption of a given system. As of now, the system only consists of 1 Distribution Server and N Leaf Servers. The Distribution Server distributes the packets to the Leaf Servers. The EnergyTailLatency is built on top of the CoreClock Simulator making the code very bloated. There are settings that may not be necessary, but are still in the code. I will slowly clean the code up, so the EnergyTailLatency Simulator stands alone. 

Important Note: The simulation runs in ms. All the numbers seen have been converted to be in ms.

Running CoreClock Simulator
---------------------------

A anaconda environment "py_conda_env.yml" is provided to create the required environment. `Download Miniconda <http://conda.pydata.org/miniconda.html>`_ Miniconda2 vs Miniconda3 doesn't really matter. To recreate the environment, open a terminal and run "conda env create -f environment.yml". The file is likely a bit out of date, but if it works, it works.

Note: The current yml file may not necessarily contain all the packages needed to run the simulation. On Windows, uncomment the lines that were commented. These packages were Windows Dependent. On Linux, use the current yml file and add packages as needed. 

Running the code
^^^^^^^^^^^^^^^^
To Run: Run CCRunner.py with an ini file as the sole argument. A sample ini file is provided ("abstract.ini"). The ini file contains all the configurations for the simulation. In Pycharm, at the top right is the configurations dropdown. You can "Edit Configurations" and add new ones as needed. I generally use two.

For all configurations, make sure the interpreter is pointing to the conda-created environment (Something like C:\Miniconda2\envs\py2_ghosal\python.exe for windows)

1) CCRunner configuration

Script: CCRunner.py

Script parameters: Abstract.ini

Full Command: python CCRunner.py Energy.ini 

Simulation Overview
-------------------

The overall simulation works using Simpy, a python library for simulation. It is complex, but the only thing that really matters is the simpy environment (stored in simenv.py). The simulation is asynchronous (each host runs its own "threads" -- one for arrivals and one for computation). They aren't really threads, but simpy makes the programming feel that way. env.timeout will sleep a thread for a given amount of time--this is how we simulation computation, packet arrival, etc. For example, if a host is "generating" data, it will predetermine the time until the next packet arrival through sampling a distribution, and the sleep (using env.timeout) for that long. Simpy will automatically wake up the "thread" and continue where it left off. This is why you will see a lot of functions surrounded by "while True:". Think of each of these functions as an async "thread".

There are a few files that make up the core of the simulation.

CCRunner.py
^^^^^^^^^^^

The starting point of the program. It calls CCSimulator.py.

CCSimulator.py
^^^^^^^^^^^^^^

run(): runs the simulation, and create the csv file. 

create_config_dict(): It's a huge function, but very simple. The parser given is a ConfigParser.SafeConfigParser() that can read the ini file. This function just converts all the ini data into a configuration dictionary that is passed around to everything for simulation setup. There are also some hard-coded default values in case the ini file doesn't have them. Some of these settings may be used or not.

Host.py
^^^^^^^
init_hosts(config): All it does is create the servers that we need for the simulation given the settings from the config dictionary. 

get_hosts(): Returns the host list 

EnergyConstHost.py
^^^^^^^^^^^^^^^

Energy_Runner(target_timestep): Runs the simulation and is responsible for stopping it once we hit the time limit. 

find_hosts(req_arr_rate, req_size, e, d_0, s_b, s_c, pow_con_model, k_m, b, P_s, alpha, num_of_servers, problem_type, freq_setting): Using the algorithm from the theory, we can find the number of servers and frequency needed to satisfy tail latency and minimize power. 

There are two classes: DistributionHost and ProcessHost. 

  DistributionHost: The DistributionHost is responsible for creating and sending packets to the ProcessHost.  
    process_arrivals(self): This function generates the packets using the IPP (interrupted Poisson Process). The IPP is simply a model with two states where one state generates packets really quickly and the other state the packets generate slowly depending on some alpha and beta values. This is how we can create bursty traffic. After generating the packet, the distribution server randomly chooses which process server it should send the packet. 
    
    ProcessHost: The ProcessHost is responsible for processing the packets. 
      process_service(self): It'll either process the packet, go to sleep, or do nothing. 
      wake_up_server(self, env): Set the server state to booting.
      finish_booting_server(self, env, time_to_wake_up): Set server state to awake.
      sleep_server(self, env): Set server state to sleep. 

Vis_Energy.py
^^^^^^^^^^^^^^^

This outputs a csv file with raw data. The csv file format is listed below. The csv file is then processed in MATLAB. 

Energy.ini Overview
-----------------

The following configurations are listed under CC_Config. 

timesteps
  This determines how long the simulation should run. In this particular simulation, the units are in milliseconds, so 300,000 is 5     minutes.

mpip_report_type
  Leave it at Energy.
  
req_size
  This was agreed upon to be 1,000,000 bytes or 1MB. 

d_0
  Some number for the theoretical algorithm. It was set to 0.01. 

P_s
  This is the power consumption during sleep and booting stages. This is 50W. 

alpha
  Some factor for the theoretical algorithm. It's 1000 right now. 

num_of_servers
  Control the total amount of servers available to the simulation. 

e
  This is the tail latency contrainst. 0.1 means a 10ms tail latency constraint.

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

The following configurations are listed under Energy. 

The problem_type and freq_setting is only useful for running the theoretical simulation to verify the results. Almost all other cases where we are going to extend the theoretical model will involve using optimal number of servers and optimal frequency, so we should just leave the problem_type and freq_setting to 1. 

problem_type
  1: Optimal Number of Servers
  2: Min Number of Servers
  3: Max Number of Servers
  
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
