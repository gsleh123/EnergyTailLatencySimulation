CoreClock Simulator
===================

The CoreClock Simulator is a python-based simulation of variable frequency CPU computation on multi-core (HPC) systems.

Using DVFS/TurboBoost, we hypothesize a more reliable (lower tail latency) application run-time. This simulator attempts to simulate various control schemes using this idea.

Running CoreClock Simulator
---------------------------

A anaconda environment "py_conda_env.yml" is provided to create the required environment. `Download Miniconda <http://conda.pydata.org/miniconda.html>`_ Miniconda2 vs Miniconda3 doesn't really matter. To recreate the environment, open a terminal and run "conda env create -f environment.yml". The file is likely a bit out of date, but if it works, it works.

Running the code
^^^^^^^^^^^^^^^^
To Run: Run CCRunner.py with an ini file as the sole argument. A sample ini file is provided ("abstract.ini"). In Pycharm, at the top right is the configurations dropdown. You can "Edit Configurations" and add new ones as needed. I generally use two.

For all configurations, make sure the interpreter is pointing to the conda-created environment (Something like C:\Miniconda2\envs\py2_ghosal\python.exe for windows)

1) CCRunner configuration

Script: CCRunner.py

Script parameters: Abstract.ini

2) Postvis (or, post-simulation visualization)

Many times I'll save the data from a simulation and generate the data at a later time (or combine data from multiple simulations). This config does that.

Script: PostVis_Abstract.py, Vis_Abstract.py, Vis_MILC.py (depends on the simulation data, no parameters).

An optional second argument can be provided that should be a trace/mpiP file. See the ini option mpip_report_type

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

The actual class for each host. The idea was that future simulations could "inherit" this class for specific implementations. MILCHost.py does this. (Note by "inherit" I just mean copy/paste and edit, python doesn't really do inheritance).

Within each host is the core data for the simulation. The __init__ constructor takes in all the data needed to setup the host (the distribution for packet generation if generating, the computation distribution and distribution parameters, etc.). There are also a few data structures for holding values for simulation purposes (queue_size, for example, just records the size of the queue every tick). The host has one or more "threads", depending on the setup. One for generating packets, if it does, one for handling packets in the queue (computation), and usually one for logging simulation details (the queue_size recording, for example, is done in process_logging).

The "control schemes" region has some basic implementation functions for a back propagation experiment. It is complete but not very useful right now. The idea was, if there are 4 neighbors, linearly scale the freq from min_freq to max_freq based on the order of arrival (which is given by the receiver of packets sent, through back-propagation).

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
  :3: GatherAll. Host 0 collects packets. Every time host 0 receives 1 packet from all N-1 other hosts, it processes them.

Visualization
-------------

Visualization for a single simulation is done in Vis_Abstract.py or Vis_MILC.py. For vis of multiple simulations, the vis is run separately in PostVis_Abstract (didn't need it for MILC...yet).

An example of a vis spanning multiple simulations would be, how does communication/computation ratio affect the run time of the broadcast job? I generally stored the data into pickles (python's serialization format) and unpickled a bunch of simulation data to show in a vis. Under Downloads, I have put a zip of the last set of pickles I used. If you run PostVis_Abstract.py with these in data/ you should see an example of a multi-simulation vis. The examples were examining the lifetimes of packets (how many sim ticks from "birth" to "death"), depending on a variety of changing parameters (freq scaling, back propagation, etc).

The primary library of choice was Seaborn, which is an extension of matplotlib. It is not too difficult to learn, especially if you know matplotlib. You are of course free to use whatever you want. The visualizations are meant to be a tool to understand the behavior.

One fascinating vis is the Vis_MILC show_host_activity_gnatt graph. Within downloads is an example.

If any of these graph functions are confusing or you don't understand what they are accomplishing, ask Prof. Ghosal for an example. I have shared many of them with him through email.