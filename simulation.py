import os

editFileCmd = os.path.join(os.getcwd(), "editFile.py")
runCmd = os.path.join(os.getcwd(), "CCRunner.py")
realTrafficTraceFile = 'high_rate_iatimes_400.txt'

oldFreq = 2.2
newFreq = 2.2

os.system("{} {} {} {}".format('python', runCmd, 'Energy.ini', realTrafficTraceFile))

while oldFreq < 2.99:
    newFreq = oldFreq + 0.05

    textToReplace = '"freq_to_use = ' + str(oldFreq) + '"'
    textToReplaceWith = '"freq_to_use = ' + str(newFreq) + '"'

    os.system("{} {} {} {}".format('python', editFileCmd, textToReplace, textToReplaceWith))
    os.system("{} {} {} {}".format('python', runCmd, 'Energy.ini', realTrafficTraceFile))

    oldFreq = newFreq

newFreq = 2.2
textToReplace = '"freq_to_use = ' + str(oldFreq) + '"'
textToReplaceWith = '"freq_to_use = ' + str(newFreq) + '"'

os.system("{} {} {} {}".format('python', editFileCmd, textToReplace, textToReplaceWith))
