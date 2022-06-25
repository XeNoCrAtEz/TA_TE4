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
        pirDataRange = range(1, len(self.dataList[0])-2)    # data PIR ada di kolom 1 smpe 3 kolom terakhir
        self.pirSums = {i:0 for i in pirDataRange}          # menggunakan dict agar bs PIR-'1' mendeteksi brp kali?
        self.globalPos = [0, 0]
        for row in self.dataList:
            # parse data sesuai dgn format aslinya
            for i in pirDataRange: row[i] = int(row[i])
            row[-2] = float(row[-2])        # lat
            row[-1] = float(row[-1])        # lng

            for i in pirDataRange:
                self.pirSums[i] += row[i]
            self.globalPos = [self.globalPos[0]+row[-2], self.globalPos[1]+row[-1]]
        self.globalPos = [self.globalPos[0]/len(self.dataList), self.globalPos[1]/len(self.dataList)]
        self.globalPos = GlobalCoord(self.globalPos[0], self.globalPos[1])
        
        # cari nomor pir yg mendeteksi
        maxIdx = max(self.pirSums, key=self.pirSums.get)
        self.PIR = [idx%10 if idx%10 != 0 else 10 for idx in range(maxIdx-1, maxIdx+2)]
        # hitung AoA
        maxIdxValue = [self.pirSums[pirNum] for pirNum in self.PIR]
        self.AoA = calc_AoA(maxIdxValue, self.PIR) + 90

    def __str__(self) -> str:
        return (
            f"{self.filename}:\n"
            f"    PIRSums:    {[self.pirSums[k] for k in self.pirSums]}\n"
            f"    PIR:        {self.PIR}\n"
            f"    AoA:        {self.AoA}\n"
            f"    GlobalPos:  {self.globalPos}\n"
            f"    RelPos:     {self.relativePos}\n"
        )


class DetectionDataWriter(DetectionData):
    def __init__(self, filename, delimiter='\t') -> None:
        super().__init__(filename, delimiter)

        self.dataFile = open(self.filename, 'w')

        self.dataFileWriter = csv.writer(self.dataFile, delimiter=delimiter)
        
    def add_new_data(self, date, detectionResult, lat, lng):
        newdata = [date, detectionResult, lat, lng]
        self.dataFileWriter.writerow(newdata)