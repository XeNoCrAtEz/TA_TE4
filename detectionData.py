import csv
from positioning import *
from utils import *

class DetectionData:
    def __init__(self, filename, delimiter='\t') -> None:
        self.filename = filename
        self.dataFile = None

    def __del__(self) -> None:
        if self.dataFile is not None: self.dataFile.close()


class DetectionDataReader(DetectionData):
    def __init__(self, filename, delimiter='\t') -> None:
        super().__init__(filename, delimiter)

        self.dataFile = open(self.filename, 'r')

        self.dataFileReader = csv.reader(self.dataFile, delimiter=delimiter)

        self.dataList = [row for row in self.dataFileReader]

        rowCount = len(self.dataList)
        columnCount = len(self.dataList[0])

        PIRDataRange = range(1, columnCount-3)              # data PIR ada di kolom 1 smpe 3 kolom terakhir
        self.PIRSums = {i:0 for i in PIRDataRange}          # menggunakan dict agar bs PIR-'1' mendeteksi brp kali?
        
        self.globalPos = [0, 0]
        self.yaw = 0
        for row in self.dataList:
            # parse data sesuai dgn format aslinya
            for i in PIRDataRange: row[i] = int(row[i])
            row[-3] = float(row[-3])        # lat: float
            row[-2] = float(row[-2])        # lng: float
            row[-1] = float(row[-1])        # yaw: float

            for i in PIRDataRange: self.PIRSums[i] += row[i]
            self.globalPos = [self.globalPos[0]+row[-3], self.globalPos[1]+row[-2]]
            
            self.yaw += row[-1]
        
        self.globalPos = [self.globalPos[0]/rowCount, self.globalPos[1]/rowCount]
        self.globalPos = GlobalCoord(self.globalPos[0], self.globalPos[1])
        
        self.yaw /= rowCount
        
        # cari nomor pir yg mendeteksi
        maxIdx = max(self.PIRSums, key=self.PIRSums.get)
        PIRcount = columnCount-4
        self.PIR = [idx%PIRcount if idx%PIRcount != 0 else PIRcount for idx in range(maxIdx-1, maxIdx+2)]
        
        # hitung AoA
        maxIdxValue = [self.PIRSums[PIRNum] for PIRNum in self.PIR]
        # TODO: PIR1 tdk pas berada di bagian kanan drone (agak ke atas dikit)
        #       Sebaiknya diganti kode kalkulasi AoA-nya, mungkin bs mskkan
        #       sudut referensi
        self.AoA = calc_AoA(maxIdxValue, self.PIR) + self.yaw

    def __str__(self) -> str:
        returnString = (
            f"{self.filename}:\n"
            f"    PIRSums:    {[self.PIRSums[k] for k in self.PIRSums]}\n"
            f"    PIR:        {self.PIR}\n"
            f"    AoA:        {self.AoA}\n"
            f"    GlobalPos:  {self.globalPos}\n"
        )
        try:
            return returnString + (
                f"    RelPos:     {self.relativePos}\n"
            )
        except AttributeError:
            return returnString + (
                f"    RelPos:     None\n"
            )


class DetectionDataWriter(DetectionData):
    def __init__(self, filename, delimiter='\t') -> None:
        super().__init__(filename, delimiter)

        self.dataFile = open(self.filename, 'w')

        self.dataFileWriter = csv.writer(self.dataFile, delimiter=delimiter)
        
    def add_new_data(self, date:str, detectionResult:list, lat:float, lng:float, yaw:float):
        newdata = [date,] + detectionResult + [lat, lng, yaw]
        self.dataFileWriter.writerow(newdata)