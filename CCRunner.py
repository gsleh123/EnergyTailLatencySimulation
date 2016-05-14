import sys
import ConfigParser
import logging

import CCSimulator


def main():

    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

    if len(sys.argv) != 2:
        print "1 argument needed: path-to-config-file"
        return 1

    config_filename = sys.argv[1]
    parser = ConfigParser.SafeConfigParser()
    parser.read(config_filename)

    CCSimulator.run(parser)


if __name__ == '__main__':
    main()
