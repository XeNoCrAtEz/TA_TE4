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
"""
import sys
from pir import *
from gps import *
from utils import *

# INITIALIZE REQUIRED VARIABLES
# argument parsing
filename = sys.argv[1]
updateTime = int(sys.argv[2])
samplingTimeout = int(sys.argv[3])

print(color_text("Initializing System\n", "green"))

print("Initialize PIR system...", end="")
# PIR pin settings
#      PIR 1  2   3   4   5   6   7   8   9   10
pin_PIR = (4, 17, 27, 22, 10, 11, 0, 24, 23, 18)
# PIR system object
PIRsys = PIR(pin_PIR, 10, 360, updateTime)
for thread in PIRsys.PIRSamplingThreads:
    if thread.is_alive(): continue
    else: raise RuntimeError("PIR sampling thread failed to run!")
print("\u001b[32mSuccess\u001b[0m")


print("Initialize drone...", end="")


print("Initialize GPS system...", end="")
# GPS system object
GPSsys = GPS(isUsingMAVLink=True)
if GPSsys.GPSSamplingThread.is_alive(): print("\u001b[32mSuccess\u001b[0m")
else: raise RuntimeError("GPS sampling thread failed to run!")