from simenv import get_env
import Host

def EnergyRunner(target_timestep):
    env = get_env()
    while env.now < target_timestep:
        yield env.timeout(1)

    for host in Host.get_hosts():
        queue_size = host.packets.qsize()
	if hasattr(host, 'packets_gather'):
            for q in host.packets_gather.values():
	        queue_size += q.qsize()

    for host in Host.get_hosts():
        host.end_sim(env)
