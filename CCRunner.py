import sys
import ConfigParser
import logging
import CCSimulator

def main():
	#with open('CCRunner_Logs1.log', 'w'):
	#	pass
	
	#logging.basicConfig(filename = "CCRunner_Logs.log", format="%(levelname)s:%(message)s", level=logging.DEBUG)
	

	if len(sys.argv) != 2 and len(sys.argv) != 3:
		print "At least 1 argument needed: path-to-config-file"
		return 1

	config_filename = sys.argv[1]
	parser = ConfigParser.SafeConfigParser()
	parser.read(config_filename)
	
	CCSimulator.run(parser)


if __name__ == '__main__':
	main()
