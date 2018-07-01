from simenv import get_env
import time
import Vis_Energy
import Host
import CreateConfigDict

def run(parser):	
	config = CreateConfigDict.create_config_dict(parser)
	
	config['timescalar'] = 1/1.
	report_type = config['mpip_report_type']

	env = get_env()
	proc = Host.init_hosts(config)

	Vis_Energy.setup()
		
	time.sleep(1)

	env.run(proc)

	Vis_Energy.show_graphs(config)
