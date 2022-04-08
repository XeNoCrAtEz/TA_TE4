import RPi.GPIO as GPIO
import threading
from time import time, sleep
from functions import normalize_data

GPIO.setmode(GPIO.BCM)

class PIR:
    def __init__(self, pin_PIR:list, updateTime:float = 1, samplingFreq:float = 10) -> None:
        self.pin_PIR = pin_PIR
        self.detectionResult = [0 for _ in pin_PIR]
        self.updateTime = updateTime
        self.samplingFreq = samplingFreq
        self.PIRlock = threading.Lock()
        self.PIRSamplingThread = threading.Thread(target=self.sample_PIR, daemon=True)

        for pinNum in pin_PIR: GPIO.setup(pinNum, GPIO.IN)

        self.PIRSamplingThread.start()

    def sample_PIR(self) -> None:
        detectionFreq = [0 for _ in self.pin_PIR]
        sampledResult = [0 for _ in self.pin_PIR]
        numSamples = 0
        samplingFreq = self.samplingFreq   # Hz
        samplingPeriod = 1/samplingFreq
        endTime = time() + self.updateTime
        while True:
            sampledResult = [GPIO.input(pinNum) for pinNum in self.pin_PIR]
            numSamples += 1
            for idx, result in enumerate(sampledResult):
                detectionFreq[idx] += result
            sleep(samplingPeriod)
            
            if time() > endTime:
                
                with self.PIRlock:
                    self.detectionResult = normalize_data(detectionFreq)

                # reset detection results
                detectionFreq = [0 for _ in self.pin_PIR]
                numSamples = 0
                endTime = time() + self.updateTime

    def get_detection_result(self) -> list:
        with self.PIRlock:
            return self.detectionResult