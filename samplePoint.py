"""
Run this module to sample PIR sensors at a point.
NOTE
----
if no GPS, use these command:
sudo systemctl restart serial-getty@ttyAMA0.service
sudo systemctl stop serial-getty@ttyAMA0.service
sudo systemctl disable serial-getty@ttyAMA0.service
"""

from time import time, ctime, sleep
import csv
import os
from pir import *
from gps import *
# from detectionData import *

def samplePoint(filename:str, updateTime:int, samplingTimeout:int, PIRsys:PIR, GPSsys:GPS):
    csvUpdateTime = time() + updateTime
    samplingTime = time() + samplingTimeout     # sample this point for 60 seconds
    resultdir = "detection_results"
    if not os.path.isdir(resultdir):
        os.mkdir(resultdir)
    csvFilename = os.path.join(resultdir, filename)
    with open(csvFilename, mode='w') as resultFile:
        CSVWriter = csv.writer(resultFile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        print("\nCollecting data...")
        print('[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]')
        # mainloop
        while True:
            # get data
            detectionResult = PIRsys.get_detection_result()
            AoA = PIRsys.calc_AoA()
            lat, lng = GPSsys.get_lat_lng()

            resultStr = "["
            for value in detectionResult:
                if value == 0:
                    resultStr += '{}, '.format(value)
                else:
                    resultStr += '\u001b[31m{}\u001b[0m, '.format(value)
            resultStr += '\b\b ]     AoA: {}\n'.format(AoA)
            resultStr += 'lat: {:.12f} lng: {:.12f}'.format(lat, lng)
            print(resultStr, end='\r\033[F')        # for re-printing resultStr at the same place
            sleep(0.5)
            # write to csv file if something detected, update per second
            if time() > csvUpdateTime:
                row = [ctime(time()),]
                row.extend(detectionResult)
                row.extend([lat,lng,AoA])
                CSVWriter.writerow(row)
                csvUpdateTime = time() + 1

            if time() > samplingTime:
                print("\n\n\n\u001b[32mData collection Done!\u001b[0m\n")
                break