import serial
import threading
import pynmea2
from time import sleep
import dronekit

class GPS:
    """
    A class that represents the GPS system. When instanced, it creates a new thread
    that runs continuously on the background, taking latitude and longitude data from
    the GPS.

    Attributes
    ----------
    isUsingMAVLink : bool
        True if GPS reading is gained from Flight Controller at the specified serial port
        False if GPS module is directly connected to the specified serial port
    port : str
        Specifies the path to Serial port filestream
    UAV : dronekit.Vehicle
        The UAV's dronekit Vehicle Object
    ser : serial.Serial()
        Serial object for communicating with the GPS
        (default baudrate is 9600, default timeout is 0.5)
    lat, lng : float, float
        The received latitude and longitude data
    GPSlock = threading.Lock()
        A lock to prevent race condition when read/writing "lat, lng"
    GPSSamplingThread = threading.Thread()
        A Thread object for receiving GPS data and update "lat, lng" continuously
        on the background

    Methods
    -------
    sample_GPS() -> None
        Receive GPS data and update "lat, lng" continuously forever until
        main program is terminated. No need to call it explicitly as it is automatically
        called by the Thread object at __init__
    get_lat_lng() -> list
        returns the latest "lat, lng" received from the GPS
    """

    def __init__(self, isUsingMAVLink: bool = True, port: str ="/dev/serial0") -> None:
        """
        Parameters
        ----------
        isUsingMAVLink : bool
            - Input True if GPS reading is gained from Flight Controller at the 
              specified serial port (default, baudrate=230400).
            - Input False if GPS module is directly connected to the specified serial port
        port : str
            Specifies the path to Serial port filestream
            (default is Serial0 => "/dev/serial0")
        """

        self.isUsingMAVLink = isUsingMAVLink

        self.port = port

        if isUsingMAVLink:
            self.UAV = dronekit.connect(self.port, baud=230400, wait_ready=False)
        else:
            self.ser = serial.Serial(self.port, baudrate=9600, timeout=0.5)
            
        self.lat, self.lng = 0, 0

        self.GPSlock = threading.Lock()
        self.GPSSamplingThread = threading.Thread(target=self.sample_GPS, daemon=True)
        self.GPSSamplingThread.start()

        sleep(2)    # let gps initialize

    def sample_GPS(self) -> None:
        """
        Get the GPS latitude and longitude data and update the result.
        """
        if self.isUsingMAVLink:
            while True:
                with self.GPSlock:
                    self.lat = self.UAV.location.global_relative_frame.lat
                    self.lng = self.UAV.location.global_relative_frame.lon
                sleep(1)
        else:
            while True:
                # get readline until "$GNRMC"
                newdata = str(self.ser.readline(), errors='ignore')
                while newdata[0:6] != "$GNRMC":
                    newdata = str(self.ser.readline(), errors='ignore')

                newmsg = pynmea2.parse(newdata)
                with self.GPSlock:
                    self.lat, self.lng = newmsg.latitude, newmsg.longitude

    def get_lat_lng(self) -> list:
        """
        Returns the latest latitude longitude value.
        """

        with self.GPSlock:
            return [self.lat, self.lng]

    def __del__(self):
        try:
            self.UAV.close()
        except AttributeError:
            self.ser.close()