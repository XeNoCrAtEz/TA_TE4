"""
Run this module to sample PIR sensors at a point for a given time (in seconds).

When running this module, it needs three command line arguments:
    * first argument:
        specifies sampling point number. The resulting csv file will be named based
        on this argument
    * second argument:
        Specifies how long the PIR system collects data before updating its output
        (in seconds)
    * third argument:
        Specifies how long the system will sample a point (in seconds)

NOTE
----
if no GPS, use these command:
sudo systemctl restart serial-getty@ttyAMA0.service
sudo systemctl stop serial-getty@ttyAMA0.service
sudo systemctl disable serial-getty@ttyAMA0.service
"""

from time import time, sleep, ctime
import csv
import numpy as np
from pir import *
from gps import *
from myObjects import *
from functions import *
import sys


# argument parsing
pointNum = int(sys.argv[1])
updateTime = int(sys.argv[2])
samplingTimeout = int(sys.argv[3])

# PIR pin settings
#      PIR 1  2  3  4   5   6   7   8   9   10
pin_PIR = (2, 3, 4, 17, 27, 22, 10, 24, 23, 18)
# delta theta for calculating AoA
deltaTheta = 360 / len(pin_PIR)
# PIR system object
PIRsys = PIR(pin_PIR, updateTime, 100)

# GPS system object
GPSsys = GPS()

csvUpdateTime = time() + updateTime
samplingTime = time() + samplingTimeout     # sample this point for 60 seconds
# mainloop
while True:
    # get data
    detectionResult = PIRsys.get_detection_result()
    AoA = PIRsys.calc_AoA()
    lat, lng = GPSsys.get_lat_lng()

    resultStr = '{}   lat: {:.12f} lng: {:.12f}   AoA: {}'.format(detectionResult, lat, lng, AoA)
    print(resultStr, end='\r')

    # write to csv file if something detected, update per second
    if time() > csvUpdateTime:
        if AoA is not None:
            csvFilename = 'detection_results/' + 'result' + str(pointNum) + '.csv'
            with open(csvFilename, mode='w') as resultFile:
                CSVWriter = csv.writer(resultFile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                CSVWriter.writerow([ctime(time()), detectionResult, lat, lng, AoA])
        csvUpdateTime = time() + 1

    if time() > samplingTime:
        break