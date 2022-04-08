import RPi.GPIO as GPIO
import threading
from time import time, sleep
from functions import normalize_data
import numpy as np

GPIO.setmode(GPIO.BCM)

class PIR: # TODO: update docstrings
    """
    A class that represents the PIR system. When instanced, it creates a new thread
    that runs continuously on the background, sampling all the PIR sensor, and updates
    the output periodically.

    Attributes
    ----------
    pin_PIR : list[int]
        List of GPIO pin number (in BCM) where the PIR0..n are connected
    detectionResult : list[bool]
        Output pattern of the PIR
    updateTime : float
        PIR system will update its "detectionResult" every "updateTime" seconds
    samplingFreq : float
        PIR system will sample the PIRs output at "samplingFreq" Hz
    PIRlock : threading.Lock()
        A lock to prevent race condition when read/writing "detectionResult"
    PIRSamplingThread : threading.Thread()
        A Thread object for sampling PIRs and update "detectionResult" continuously
        on the background

    Methods
    -------
    sample_PIR() -> None
        Sampling PIR outputs and update "detectionResult" continuously forever until
        main program is terminated. No need to call it explicitly as it is automatically
        called by the Thread object at __init__
    get_detection_result() -> list
        returns the latest "detectionResult" of the PIRs
    """

    def __init__(
            self, pin_PIR:list, V: np.ndarray() = None,
            updateTime:float = 1, samplingFreq:float = 10
    ) -> None:
        """
        Parameters
        ----------
        pin_PIR : list[int]
            List of GPIO pin number (in BCM) where PIR0..n is connected
        V : np.ndarray()
            PIR visibility matrix (default is None, which means the visibility matrix
            is an identity matrix)
        updateTime : float, optional
            Specifies when to update "detectionResult" in seconds (default is 1)
        samplingFreq : int, optional
            Specifies sampling frequency of PIRs in Hz (default is 10)
        """

        self.pin_PIR = pin_PIR

        self.detectionResult = [0 for _ in pin_PIR]
        self.V = V if V is not None else np.identity(len(pin_PIR))
        self.m = self.get_output_pattern()
        self.s = self.get_detection_pattern()

        self.updateTime = updateTime
        self.samplingFreq = samplingFreq
        self.PIRlock = threading.Lock()
        self.PIRSamplingThread = threading.Thread(target=self.sample_PIR, daemon=True)

        for pinNum in pin_PIR: GPIO.setup(pinNum, GPIO.IN)

        self.PIRSamplingThread.start()

    def sample_PIR(self) -> None:
        """
        Samples the PIR sensors at the specified sampling frequency and updates the
        result periodically. The sampling result is normalized using min-max normalization
        to reduce noise / false triggers.
        """

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
                    self.s = np.dot(np.linalg.inv(self.V), self.m).astype(bool)

                # reset detection results
                detectionFreq = [0 for _ in self.pin_PIR]
                numSamples = 0
                endTime = time() + self.updateTime

    def get_detection_result(self) -> list:
        """
        Returns the latest detection result.
        """
        
        with self.PIRlock:
            return self.detectionResult

    def calc_output_pattern(self) -> np.ndarray:
        """
        returns the latest output pattern m (as a numpy array)
        """

        return np.transpose(np.array(self.get_detection_result(), dtype=bool))
    
    def get_output_pattern(self) -> np.ndarray:
        """
        returns the latest output pattern m (as a numpy array)
        """

        with self.PIRlock:
            return self.m

    def get_detection_pattern(self) -> np.ndarray:
        """
        returns detection pattern s of the PIR system (s = m * V)

        """
        
        with self.PIRlock:
            return self.s