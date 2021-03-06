import RPi.GPIO as GPIO
import threading
import numpy as np

GPIO.setmode(GPIO.BCM)

class PIR:
    """
    A class that represents general PIR system. When instanced, it creates a new thread
    that runs continuously on the background, sampling all the PIR sensor, and updates
    the output periodically.

    Attributes
    ----------
    pin_PIR : list[int]
        List of GPIO pin number (in BCM) where the PIR0..n are connected
    k : int
        Number of PIR sensor
    FOV : float
        Bearing sensor's Field-of-View
    n : int
        Number of fan-shaped detection cells on this PIR system
    deltaTheta : float
        Angle size of each fan-shaped cells
    V : np.ndarray
        Bearing sensor's Visibility matrix
    detectionResult : list[bool]
        Output pattern of the PIRs (as python's list object)
    m : np.ndarray
        Output pattern of the PIRs (as numpy array)
    s : np.ndarray
        Detection pattern of the bearing sensor
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
            self, pin_PIR: list, n: int, FOV: float,
            updateTime: float = 1, samplingFreq: float = 10
    ) -> None:
        """
        Parameters
        ----------
        pin_PIR : list[int]
            List of GPIO pin number (in BCM) where PIR0..k is connected
        n : int
            Number of fan-shaped detection cells on this PIR system
        FOV : float
            PIR system Field-of-View
        updateTime : float, optional
            Specifies when to update "detectionResult" in seconds (default is 1)
        samplingFreq : int, optional
            Specifies sampling frequency of PIRs in Hz (default is 10)
        """

        # PIR system attributes
        self.pin_PIR = pin_PIR
        self.k = len(pin_PIR)

        self.FOV = FOV
        self.n = n
        self.deltaTheta = FOV/n

        self.V = self.calc_V()

        # PIR system result attributes
        self.detectionResult = [0 for _ in pin_PIR]
        self.m = np.array([])
        self.s = np.array([])

        self.updateTime = updateTime
        self.samplingFreq = samplingFreq
        self.PIRlock = threading.Lock()
        self.stopThread = threading.Event()

        self.PIRSamplingThreads = []

        for pinIdx, pinNum in enumerate(pin_PIR):
            GPIO.setup(pinNum, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            self.PIRSamplingThreads.append(threading.Thread(target=self.sample_PIR, args=(pinIdx,pinNum), daemon=True))
            self.PIRSamplingThreads[-1].start()

    def sample_PIR(self, pinIdx, pinNum) -> None:
        """
        Samples the PIR sensors at the specified sampling frequency and updates the
        result periodically. The sampling result is normalized using min-max normalization
        to reduce noise / false triggers.
        """

        isDetected = False
        while True:
            if self.stopThread.is_set():
                break
            pirOutput = GPIO.input(pinNum)
            if isDetected == False:
                if pirOutput == 0: continue
                isDetected = True
                with self.PIRlock:
                    self.detectionResult[pinIdx] = pirOutput
                    self.m = np.transpose(np.array(self.detectionResult, dtype=bool))
                    self.s = np.dot(np.linalg.inv(self.V), self.m).astype(bool)
            if isDetected == True:
                if pirOutput == 1: continue
                isDetected = False
                with self.PIRlock:
                    self.detectionResult[pinIdx] = pirOutput
                    self.m = np.transpose(np.array(self.detectionResult, dtype=bool))
                    self.s = np.dot(np.linalg.inv(self.V), self.m).astype(bool)

    def calc_V(self) -> np.ndarray:
        """
        Returns the appropriate visibility matrix for the specified number of
        fan-shaped detection cells and PIR count. Currently only supports calculating
        for same number of fan-shaped cells and PIR count.
        """

        if self.k == self.n: return np.identity(self.k)
        else: raise NotImplementedError

    def get_detection_result(self) -> list:
        """
        Returns the latest detection result.
        """
        
        with self.PIRlock:
            return self.detectionResult

    
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

    def calc_AoA(self) -> float:
        """
        Calculate AoA (in degree) for the given detection pattern s and fan-shaped cell
        detection angle (in degree)

        NOTE
        -------
        FOV of 360 has different cell numbering than <360. For 360, C1 starts from 0 deg

        Returns
        -------
        float
            AoA value of the given detection pattern
        None
            If the given detection pattern does not match any AoA value
        """

        s = np.transpose(self.get_detection_pattern()).tolist()
        n = len(s)
        sparsity = np.count_nonzero(s)
        startAngle = (180 - self.FOV)/2
        if sparsity == 1:
            i = s.index(True)
            if self.FOV != 360: return (i + i + 1) * self.deltaTheta / 2 + startAngle
            else: return (i + i + 1) * self.deltaTheta / 2
        elif sparsity == 2:
            for i in range(n):
                if [s[i-1], s[i]] == [True, True]:
                    if self.FOV != 360: return ((i-1 % n) + (i + 1)) * self.deltaTheta / 2 + startAngle
                    else: return ((i-1 % n) + (i + 1)) * self.deltaTheta / 2
        else: return None

    def __del__(self):
        self.stopThread.set()
        GPIO.cleanup()