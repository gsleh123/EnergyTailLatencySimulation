import logging
from simenv import get_env
import numpy as np
from collections import namedtuple
from Packet import Packet
from MILCHost import MILCHost

hosts = []

lognormal_param = namedtuple('lognormal_param', 'mean sigma')


def init_hosts(config):
    global hosts
    global num_of_hosts

    hosts = []
    num_of_hosts = config['host_count']

    for i in range(num_of_hosts):
        if config['mpip_report_type'] == 'MILC':
            arrival_distributions, service_lognormal_param = __load_mpip_report()
            hosts.append(MILCHost(i, config, arrival_distributions, service_lognormal_param))
            get_env().process(hosts[i].process())
        # else:
        #     hosts.append(Host(i, config))
        #     get_env().process(hosts[i].packet_arrival())
        #     get_env().process(hosts[i].packet_service())


def get_hosts():
    global hosts
    return hosts


def __load_mpip_report():

    # todo: read milc filepath from config file
    # for now just hardcode the sample

    with open('data/node4_sample/su3_rmd.128.9161.1.mpiP') as file:
        lines = [line.rstrip('\n') for line in file]

    avg_mean = 0.
    avg_sigma = 0.
    entry_count = 0

    # to return
    arrival_distributions = dict()

    line_number = 0
    line = lines[line_number]
    while not line.startswith('@--- Callsite Time statistics'):
        line_number += 1
        line = lines[line_number]

    # now we are at the callsite stats. finish skipping the header
    line_number += 3
    line = lines[line_number]  # this is the first callsite line
    while not line.startswith('-'):

        split = line.split()  # whitespace is default

        if len(line) < 2 or len(split) < 8:
            line_number += 1
            line = lines[line_number]
            continue

        mpi_call_type = split[0]
        site = int(split[1])
        if split[2].startswith('*'):  # the "all" line
            line_number += 1
            line = lines[line_number]
            continue
        rank = int(split[2])
        count = int(split[3])
        max = float(split[4])
        mean = float(split[5])
        min = float(split[6])
        app_percent = float(split[7])
        mpi_percent = float(split[8])

        # we are focusing on call site 2 for MPI_Isend and call site 11 for MPI_Allreduce
        if site not in [2, 11]:
            line_number += 1
            line = lines[line_number]
            continue

        if site is 2:  # MPI_ISend
            pass
        elif site is 11:  # MPI_Allreduce
            pass  # todo

        line_number += 1
        line = lines[line_number]

        # try to estimate the lognormal distribution's sigma, given the max, min as 95%.
        sigma = mean - min  # NOT CORRECT!
        logging.info('%i %f', rank, sigma)

        avg_mean += mean
        avg_sigma += sigma
        entry_count += 1

        arrival_distributions[rank] = lognormal_param(mean*200, sigma*200)

    # we need to calculate the average mean and sigma to use for computation time
    service_lognormal_param = lognormal_param(avg_mean/entry_count, avg_sigma/entry_count)

    return arrival_distributions, service_lognormal_param
