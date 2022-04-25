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

from time import time, ctime
import csv
from pir import *
from gps import *
from myObjects import *
from functions import *
import sys


# argument parsing
pointNum = int(sys.argv[1])
updateTime = int(sys.argv[2])
samplingTimeout = int(sys.argv[3])

print("Initialize PIR system...", end="")

# PIR pin settings
#      PIR 1  2  3  4   5   6   7   8   9   10
pin_PIR = (2, 3, 4, 17, 27, 22, 10, 24, 23, 18)
# delta theta for calculating AoA
deltaTheta = 360 / len(pin_PIR)
# PIR system object
PIRsys = PIR(pin_PIR, 10, 360, updateTime)

if PIRsys.PIRSamplingThread.is_alive(): print("\u001b[32mSuccess\u001b[0m")
else: raise RuntimeError("PIR sampling thread failed to run!")

print("Initialize GPS system...", end="")

# GPS system object
GPSsys = GPS()

if GPSsys.GPSSamplingThread.is_alive(): print("\u001b[32mSuccess\u001b[0m")
else: raise RuntimeError("GPS sampling thread failed to run!")

csvUpdateTime = time() + updateTime
samplingTime = time() + samplingTimeout     # sample this point for 60 seconds
csvFilename = 'detection_results/' + 'result' + str(pointNum) + '.csv'
with open(csvFilename, mode='w') as resultFile:
    CSVWriter = csv.writer(resultFile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    print("\nCollecting data...")
    # mainloop
    while True:
        # get data
        detectionResult = PIRsys.get_detection_result()
        AoA = PIRsys.calc_AoA()
        lat, lng = GPSsys.get_lat_lng()

        resultStr = '{}     AoA: {}\n'.format(detectionResult, AoA)
        resultStr += 'lat: {:.12f} lng: {:.12f}'.format(lat, lng)
        print(resultStr, end='\r\033[F')        # for re-printing resultStr at the same place

        # write to csv file if something detected, update per second
        if time() > csvUpdateTime:
            if AoA is not None: CSVWriter.writerow([ctime(time()), detectionResult, lat, lng, AoA])
            csvUpdateTime = time() + 1

        if time() > samplingTime:
            print("\n\n\n\u001b[32mData collection Done!\u001b[0m\n")
            break