import fileinput
import sys

fileToSearch = 'Energy.ini'
textToSearch = sys.argv[1]
textToReplace = sys.argv[2]

f = fileinput.FileInput(fileToSearch, inplace = True, backup = '.bak')

for line in f:
	sys.stdout.write(line.replace(textToSearch, textToReplace))

f.close()

