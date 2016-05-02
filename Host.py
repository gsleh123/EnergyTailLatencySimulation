import logging
from simenv import get_env
import numpy as np
from collections import namedtuple
import itertools
import MILCHost

hosts = []

lognormal_param = namedtuple('lognormal_param', 'mean sigma')


def init_hosts(config):
    global hosts
    global num_of_hosts

    hosts = []
    num_of_hosts = config['host_count']

    host_to_dimension, dimension_to_host = __generate_rank_to_dimension_lookup(
         config['host_count'], config['MILC']['dimensions'])

    for i in range(num_of_hosts):
        if config['mpip_report_type'] == 'MILC':
            isend_distributions, allreduce_distributions, service_lognormal_param, raw_data = __load_mpip_report(config)
            hosts.append(MILCHost.MILCHost(i, config,
                                           isend_distributions, allreduce_distributions, service_lognormal_param,
                                           host_to_dimension[i], dimension_to_host))

    for i in np.random.permutation(num_of_hosts):
        get_env().process(hosts[i].process())

    target_timestep = config['timesteps']
    return get_env().process(MILCHost.MILC_Runner(target_timestep))


def get_hosts():
    global hosts
    return hosts


def __generate_rank_to_dimension_lookup(host_count, problem_dimensions):
    """
    create a lookup (and reverse lookup) table between rank and dimension
    """
    # Note, since itertools.product starts with the last iterable,
    # We reverse the order of the variables to match MILC
    # todo: check that problem dimensions* and host count match in size
    host_to_dimension = [None] * host_count
    dimension_to_host = dict()
    host_id = 0
    for t, z, y, x in itertools.product(range(problem_dimensions[3]), range(problem_dimensions[2]),
                                        range(problem_dimensions[1]), range(problem_dimensions[0])):
        host_to_dimension[host_id] = [x, y, z, t]
        dimension_to_host[x, y, z, t] = host_id
        host_id += 1

    return host_to_dimension, dimension_to_host


def __load_mpip_report(config):

    # todo: read milc filepath from config file
    # for now just hardcode the sample

    with open('data/node4_sample/su3_rmd.128.9161.1.mpiP') as file:
        lines = [line.rstrip('\n') for line in file]

    avg_mean = 0.
    avg_sigma = 0.
    entry_count = 0

    # to return
    allreduce_distributions = dict()
    isend_distributions = dict()
    raw_data = dict()

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
        max = float(split[4])*1000  # milliseconds -> microseconds
        mean = float(split[5])*1000  # this also makes taking the log for values < 1 work
        min = float(split[6])*1000
        app_percent = float(split[7])
        mpi_percent = float(split[8])

        # we are focusing on call site 2 for MPI_Isend and call site 11 for MPI_Allreduce
        if site not in [2, 11]:
            line_number += 1
            line = lines[line_number]
            continue

        line_number += 1
        line = lines[line_number]

        # try to estimate the lognormal distribution's sigma, given the max, min as 95%.
        # we use a naive approach: apply log to the min, mean max,
        # presume normal distribution,
        # take the exponential of the calculated sigma
        log_min = np.log(min)
        log_mean = np.log(mean)
        log_max = np.log(max)

        # sigma = np.mean([(log_min - log_mean) / -2.5, (log_max - log_mean) / 3.5])
        sigma = (log_min - log_mean) / -3
        sigma = np.exp(sigma)

        # logging.info('%i %f %f %f %f', rank, min, mean, max, sigma)

        # scaling by 1/100
        min *= config['timescalar']
        mean *= config['timescalar']
        max *= config['timescalar']
        sigma *= config['timescalar']

        avg_mean += mean
        avg_sigma += sigma
        entry_count += 1

        if rank not in raw_data:
            raw_data[rank] = dict()

        if site == 2:  # MPI_ISend
            isend_distributions[rank] = lognormal_param(mean, sigma)
            raw_data[rank]['isend'] = [min, mean, max]
        elif site == 11:  # MPI_Allreduce
            allreduce_distributions[rank] = lognormal_param(mean, sigma)
            raw_data[rank]['allreduce'] = [min, mean, max]

    # we need to calculate the average mean and sigma to use for computation time
    # todo: use the ini file variable
    service_lognormal_param = lognormal_param(avg_mean/entry_count, avg_sigma/entry_count)

    return isend_distributions, allreduce_distributions, service_lognormal_param, raw_data
