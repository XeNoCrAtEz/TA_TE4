"""
Main code for TA_TE-4

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

Before running this script, please run mavproxy first using this command:
mavproxy.py --master=/dev/serial0,912600 --out=udp:127.0.0.1:14550
"""
import sys
from time import sleep
from pir import *
from gps import *
from utils import *
from samplePoint import *
import dronekit

# INITIALIZE REQUIRED VARIABLES
# argument parsing
filename = sys.argv[1]
updateTime = int(sys.argv[2])
samplingTimeout = int(sys.argv[3])

print(color_text("Initializing System...\n", "green"))

print("Initialize PIR system...", end="")
# PIR pin settings
#      PIR 1  2   3   4   5   6   7   8   9   10
pin_PIR = (4, 17, 27, 22, 10, 11, 0 , 24, 23, 18)
# PIR system object
PIRsys = PIR(pin_PIR, 10, 360, updateTime)
for thread in PIRsys.PIRSamplingThreads:
    if thread.is_alive(): continue
    else: raise RuntimeError("PIR sampling thread failed to run!")
print(color_text("Success\n", "green"))

print("Initialize drone...", end="")
mavproxyOut = sys.argv[4]
# Drone system object
UAV = dronekit.connect(mavproxyOut, wait_ready=False)
if UAV is not None: print(color_text("Success", "green"))
else: raise RuntimeError("Failed to connect to drone")
# print drone data
print("Battery: " + color_text(f"{UAV.battery}", "blue"))
print("System status: " + color_text(f"{UAV.system_status.state}", "blue"))
print("Mode " + color_text(f"{UAV.mode}", "blue"))
print("")

print("Initialize GPS system...", end="")
# GPS system object
GPSsys = GPS(UAV, mavproxyOut)
if GPSsys.GPSSamplingThread.is_alive(): print(color_text("Success\n", "green"))
else: raise RuntimeError("GPS sampling thread failed to run!")

print(color_text("System Initialization Completed\n", "green"))

# SAMPLE AT EACH POINT
print(color_text(f"Sampling Data for {filename}...\n", "green"))
# tunggu hingga drone di arm
print("Waiting for UAV to be armed...", end="")
while not UAV.armed:
    sleep(0.5)
print(color_text("Armed", "red"))

# # tunggu hingga drone dlm mode auto
# print("Waiting for UAV to be in AUTO mode...", end="")
# while UAV.mode.name != "AUTO":
#     sleep(1)
# print(color_text("AUTO mode", "red"))

# tunggu hingga drone dlm mode loiter (pendeteksian dimulai)
print("Waiting for UAV to be in LOITER mode...", end="")
while not UAV.mode.name == 'LOITER':
    sleep(0.5)
print(color_text("LOITER mode", "red"))

# sample data
print(f"Sampling data for {filename}...", end="")
resultdir = "detection_results"
samplePoint(filename, resultdir, updateTime, samplingTimeout, PIRsys, GPSsys, UAV)

print(color_text("Sampling Points Completed\n", "green"))

# # TRIANGULATE ALL THE DATA
# print(color_text("Triangulating All The Data...\n", "green"))

# print(color_text("System Completed!", "green"))