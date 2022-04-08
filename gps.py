import serial
import threading
import pynmea2

class GPS:
    def __init__(self) -> None:
        self.port = "/dev/serial0"
        self.ser = serial.Serial(self.port, baudrate=9600, timeout=0.5)

        self.lat, self.lng = 0, 0

        self.GPSlock = threading.Lock()
        self.GPSSamplingThread = threading.Thread(target=self.sample_GPS, daemon=True)
        self.GPSSamplingThread.start()

    def sample_GPS(self) -> None:
        while True:
            # get readline until "$GNRMC"
            newdata = str(self.ser.readline(), errors='ignore')
            while newdata[0:6] != "$GNRMC":
                newdata = str(self.ser.readline(), errors='ignore')

            newmsg = pynmea2.parse(newdata)
            with self.GPSlock:
                self.lat, self.lng = newmsg.latitude, newmsg.longitude

    def get_lat_lng(self) -> list:
        with self.GPSlock:
            return [self.lat, self.lng]