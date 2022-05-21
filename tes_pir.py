import RPi.GPIO as GPIO
import time
import datetime

GPIO.setmode(GPIO.BCM)

GPIO.setup(2, GPIO.IN)
try:
    time.sleep(2) # to stabilize sensor
    
    stopTime = time.time() + 10
    while time.time() < stopTime:
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        
        while not GPIO.input(2):
            print("tes")
            # time.sleep(0.1) #loop delay, should be less than detection delay

        print("Motion Detected at {}".format(st))

except:
    GPIO.cleanup()
