import datetime

with open('dataInfor.txt', 'a') as outFile:
    outFile.write('\n' + str(datetime.datetime.now()))