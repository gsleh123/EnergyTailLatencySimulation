from __future__ import division
from scipy.special import lambertw
import math

def find_hosts(req_arr_rate, req_size, e, d_0, s_b, s_c, pow_con_model, k_m, b, P_s, alpha, num_of_servers, problem_type, freq_setting, servers_to_use, freq_to_use):
    min_servers = 0
    min_total_power = float('inf')
    opt_servers = 0
    opt_freq = 0
    flag = 0
    servers = num_of_servers
    gamma = (alpha * d_0) / (math.exp(-(alpha * d_0)) - e)

    # determine min_servers to satisfy tail latency
    w = lambertw(-(e / math.exp(1)), -1).real

    if (1 / d_0) * math.log(1 / e) < alpha and alpha < ((1 / d_0) * (-w - 1)):
        w = lambertw(gamma * math.exp(e * gamma)).real
        min_servers = (req_arr_rate / ((s_c / req_size) - ((1 / d_0) * (w - (e * gamma)))))
        flag = 1
    else:
        w = lambertw(gamma * math.exp(e * gamma), -1).real
        min_servers = (req_arr_rate / ((s_c / req_size) - (1 / d_0) * (w - e * gamma)))
        flag = 0

        min_servers = int(math.ceil(min_servers))

    if min_servers > num_of_servers:
        # min amount of servers needed exceeds available servers
        return -1, -1 # no feasible solution

        # depending on the problem type figure out the number of servers to use
    if problem_type == 1:
        # optimal servers
        min_servers = min_servers
        num_of_servers = num_of_servers
    elif problem_type == 2:
        # min servers
        min_servers = min_servers
        num_of_servers = min_servers
    elif problem_type == 3:
        min_servers = num_of_servers
        num_of_servers = num_of_servers

    # find optimal servers and optimal frequencies
    for i in range (min_servers, num_of_servers + 1):
        # calculate optimal frequency
        if pow_con_model == 1:
            if b - (s_b / k_m) >= P_s:
                curr_freq = s_c
            else:
                if flag:
                    w = lambertw(gamma * math.exp(e * gamma)).real
                    curr_freq = max(s_b, (((req_arr_rate / i)+ (1 / d_0) * (w - gamma*e)) * req_size))
                else:
                    w = lambertw(gamma * math.exp(e * gamma), -1).real
                    curr_freq = max(s_b, (((req_arr_rate / i)+ (1 / d_0) * (w - gamma*e)) * req_size))
        elif pow_con_model == 2:
            s_e = math.sqrt(((b - P_s)*(k_m ** 2)) + (s_b ** 2))

            if s_e > s_c:
                curr_freq = s_c
            else:
                if flag:
                    w = lambertw(gamma * math.exp(e * gamma)).real
                    temp = ((req_arr_rate / i) + (1 / d_0) * (w - gamma*e)) * req_size

                    if temp <= s_e and s_e <= s_c:
                        curr_freq = s_e
                    else:
                        curr_freq = temp
                else:
                    w = lambertw(gamma * math.exp(e * gamma), -1).real
                    temp = ((req_arr_rate / i) + ((1 / d_0) * (w - gamma*e))) * req_size

                    if temp <= s_e and s_e <= s_c:
                        curr_freq = s_e
                    else:
                        curr_freq = temp

        # calculate the power consumption of each server
        curr_total_power = (((1 / i) * req_arr_rate * req_size / curr_freq) * (b + ((curr_freq - s_b) / k_m)**pow_con_model)) + ((1 - ((1 / i) * req_arr_rate * req_size / curr_freq)) * P_s)
        curr_total_power = i * curr_total_power

                # update the optimal servers if we found a new min_total_power
        if curr_total_power < min_total_power:
            min_total_power = curr_total_power
            opt_servers = i
            opt_freq = curr_freq

    if freq_setting == 2:
        # we want the max freq which is S_c
        opt_freq = s_c

    if problem_type == 4:
        opt_servers = servers_to_use
        opt_freq = freq_to_use

    return opt_servers, opt_freq

