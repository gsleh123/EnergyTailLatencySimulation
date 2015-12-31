
import simpy
import random

from ThermalModel import ThermalSlack

env = simpy.Environment()
hosts = []
num_of_hosts = 1

def main():
    global env

    for i in range(num_of_hosts):
        hosts.append(Host(i, 0.1))
        env.process(hosts[-1].packet_arrival())
        env.process(hosts[-1].packet_process())

    env.run(until=1000000)

    print('done')


class Host(object):
    """docstring for Host"""
    def __init__(self, idd, arrival_rate):
        self.id = idd
        self.arrival_rate = arrival_rate
        self.packet_queue = 0
        self.thermal_slack = ThermalSlack()

    def packet_arrival(self):
        global env

        while True:
            yield env.timeout(random.expovariate(self.arrival_rate))

            self.packet_queue += 1
        
    def packet_process(self):
        global env

        while True:
            yield env.timeout(1)
            self.thermal_slack.Tick()


if __name__ == '__main__':
    main()
