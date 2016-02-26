import sys
import CCSimulator
import ConfigParser


def main():
    if len(sys.argv) != 2:
        print "1 argument needed: path-to-config-file"
        return 1

    config_filename = sys.argv[1]
    parser = ConfigParser.SafeConfigParser()
    parser.read(config_filename)

    CCSimulator.Run(parser)


if __name__ == '__main__':
    main()
