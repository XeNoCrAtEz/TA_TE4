"""
Run this module to sample PIR sensors at a point.
NOTE
----
if no GPS, use these command:
sudo systemctl restart serial-getty@ttyAMA0.service
sudo systemctl stop serial-getty@ttyAMA0.service
sudo systemctl disable serial-getty@ttyAMA0.service
"""

from time import time, ctime
import os
from pir import *
from gps import *
from utils import *
from detectionData import *
import dronekit

DELAY_TIME = 0.5

def samplePoint(
        filename:str, resultdir:str,
        updateTime:int, samplingTimeout:int,
        PIRsys:PIR, GPSsys:GPS, UAV:dronekit.Vehicle
    ):
    csvUpdateTime = time() + updateTime
    samplingTime = time() + samplingTimeout
    readingsRefreshTime = time() + DELAY_TIME
    
    if not os.path.isdir(resultdir):
        os.mkdir(resultdir)
    csvFilename = os.path.join(resultdir, filename)
    detectionDataWriter = DetectionDataWriter(csvFilename)

    print(
        "\n"
        "Collecting data..."
        "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]"
    )
    while True:
        if time() > readingsRefreshTime:
            detectionResult = PIRsys.get_detection_result()
            lat, lng = GPSsys.get_lat_lng()
            yaw = UAV.attitude.yaw

            resultStr = "["
            for value in detectionResult:
                if value == 0:
                    resultStr += f'{value}, '
                else:
                    resultStr += color_text(f"{value}, ", "red")
            resultStr += '\b\b ]\n'
            resultStr += f'lat: {lat:.12f} lng: {lng:.12f}'
            print(resultStr, end='\r\033[F')        # for re-printing resultStr at the same place
        
        if time() > csvUpdateTime:
            detectionDataWriter.add_new_data(
                ctime(time()), detectionResult,
                lat, lng, yaw
            )
            csvUpdateTime = time() + updateTime

        if time() > samplingTime:
            print(color_text("\n\n\nData collection Done!\n"), "green")
            break