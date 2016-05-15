CoreClock Simulator
===================

The CoreClock Simulator is a python-based simulation of variable frequency CPU computation on multi-core (HPC) systems.

Using DVFS/TurboBoost, we hypothesize a more reliable (lower tail latency) application run-time. This simulator attempts to simulate various control schemes using this idea.

Running CoreClock Simulator
---------------------------

A anaconda environment "py_conda_env.yml" is provided to create the required environment.

To Run: Run CCRunner.py with an ini file as the sole argument. A sample ini file is provided ("two_states_with_setup.ini")

An optional second argument can be provided that should be a trace/mpiP file. See the ini option mpip_report_type_

Code Overview
-------------

TODO

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
  The ratio of communication and computation time. A value of 0.5 means at freq=freq_upper_bound, the CPU spends on average 50% time on communication (sending/receiving) and 50% computing.

.. _mpip_report_type:
mpip_report_type
  This option allows for a string of an application to mimic communication traffic using. The only supported application at the moment is 'MILC'


Abstract Overview
-----------------

problem_type
  The type of problem to set up
  :1: Scatter. Host 0 generates packets, and randomly sends to another host. That host services and discards
  :2: Broadcast. Host 0 generates and services packets, then sends to all
  :3: GatherAll. Host 0 collects packets. Every time host 0 receives 1 packet from all N-1 other hosts, it processes them.