EnergyTailLatency Simulator
===================

The EnergyTailLatency Simulator is a python-based simulation of to determine the tail latency and energy consumption of a given system. As of now, the system only consists of 1 Distribution Server and N Leaf Servers. The Distribution Server distributes the packets to the Leaf Servers. The EnergyTailLatency is built on top of the CoreClock Simulator making the code very bloated. There are settings that may not be necessary, but are still in the code. I will slowly clean the code up, so the EnergyTailLatency Simulator stands alone. 

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

Full Command: python CCRunner.py Abstract.ini 

Simulation Overview
-------------------

The overall simulation works using Simpy, a python library for simulation. It is complex, but the only thing that really matters is the simpy environment (stored in simenv.py). The simulation is asynchronous (each host runs its own "threads" -- one for arrivals and one for computation). They aren't really threads, but simpy makes the programming feel that way. env.timeout will sleep a thread for a given amount of time--this is how we simulation computation, packet arrival, etc. For example, if a host is "generating" data, it will predetermine the time until the next packet arrival through sampling a distribution, and the sleep (using env.timeout) for that long. Simpy will automatically wake up the "thread" and continue where it left off. This is why you will see a lot of functions surrounded by "while True:". Think of each of these functions as an async "thread".

There are a few classes that make up the core of the simulation.

CCRunner.py
^^^^^^^^^^^

The starting point of the program.

CCSimulator.py
^^^^^^^^^^^^^^

run(): runs the simulation, and shows the visualizations. 

create_config_dict() : It's a huge function, but very simple. The parser given is a ConfigParser.SafeConfigParser() that can read the ini file. This function just converts all the ini data into a configuration dictionary that is passed around to everything for simulation setup. There are also some hard-coded default values in case the ini file doesn't have them.

Host.py
^^^^^^^

A "static" class that manages all the hosts. This file handles the initialization of hosts. Methods in this file are responsible for creating the network (who should send to who). Many are MILC specific

__generate_rank_to_dimension_lookup : Generates maps between MPI rank and a dimension coordinate (for a particular problem size). ie, for 256 nodes on a 4x4x4x4 problem, each node has a coordinate.

__load_mpip_report : mpiP is a profiler for MPI. This function reads the report and tries to recreate the setup in the simulator. There are some examples of the reports in data/node4_sample.

calculate_broadcast_setup : For rank i in a widthxdepth broadcast setup, calculate the list of hosts (rank) that this host should send to, as well as if this host is a root (should generate new packets).

AbstractHost.py
^^^^^^^^^^^^^^^

INI File Overview
-----------------

All configuration options should be under a section titled 'CC_Config'

host_count
  The number of hosts for the simulation

seed
  Random seed

freq_lower_bound
  The minimum frequency possible by the simulated CPU

freq_upper_bound
  The maximum frequency possible by the simulated CPU

arrival_rate
  The rate of the arrival stream. The inter-arrival rate is by default poisson. This rate sets the "scale" argument of the exponential distribution.

service_rate
  The rate of the service stream (per host). The default distribution is exponential.

sleep_alpha
  Modifies the time spent sleeping to "wake up" a core. Currently unused.

computation_communication_ratio
  The ratio of communication and computation time. A value of 1 means there is a 1:1 ratio of communication vs computation. Values greater than 1 mean more time is spent in communication.

mpip_report_type
  This option allows for a string of an application to mimic communication traffic using. The only supported application at the moment is 'MILC', and an abstract "application" is available using 'ABSTRACT'


Abstract Overview
-----------------

problem_type
  The type of problem to set up
  :1: Scatter. Host 0 generates packets, and randomly sends to another host. That host services and discards
  :2: Broadcast. Host 0 generates and services packets, then sends to all
<<<<<<< HEAD
  :3: GatherAll. Host 0 collects packets. Every time host 0 receives 1 packet from all N-1 other hosts, it processes them.
=======
  :3: GatherAll. Host 0 collects packets. Every time host 0 receives 1 packet from all N-1 other hosts, it processes them.

freq_setting
  :1 Optimal Frequency
  :2 Max Frequency
  
Output Overview
-------------

Visualization
-------------

The visualization is done using MATLAB using the csv data from the simulation. 
