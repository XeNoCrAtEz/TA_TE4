import subprocess
import csv
import datetime
from utils import *
import requests
from detectionData import *

detectionData = [DetectionDataReader(f"detection_results/Point{i}_5m.csv", ',') for i in range(1, 13)]
originData = detectionData[0]
originData.relativePos = originData.globalPos.to_relative(originData.globalPos)
print(originData)
for data in detectionData:
    data.relativePos = data.globalPos.to_relative(originData.globalPos)
    print(data)

isRelCoord = False
listPosKorban = [
    triangulate(originData, detectionData[4:7], isRelCoord),
    triangulate(originData, detectionData[8:11], isRelCoord)
]

for posKorban in listPosKorban:
    print(posKorban)

# error = np.sqrt((realTargetPos[0]-targetPos[0])**2 + (realTargetPos[1]-targetPos[1])**2)
print("")
# print(f"Error = {error} m")


# for i in range(3):
#     print(f"Sampling point-{i}")
#     subprocess.call(['python', 'samplePoint.py', str(i)])
#     print("\n")

# pointsPos = []
# AoAs = []
# for i in range(3):
#     csvFilename = 'detection_results/result' + str(i) + '.csv'
#     with open(csvFilename, 'r') as csv_file:
#         csv_reader = csv.reader(csv_file, delimiter='\t')
#         line_count = 0
#         for row in csv_reader:
#             timeDetected = row[0]
#             detectionResult = row[1]
#             lat = float(row[2])
#             lng = float(row[3])
#             AoA = float(row[4])
#             print(f'At time {timeDetected}:')
#             print(f'\tDetection result: {detectionResult}')
#             print(f'\tlat: {lat}  lng: {lng}')
#             print(f'\tAoA: {AoA}')

#             pointsPos.append([lat, lng])
#             AoAs.append(AoA)

#             # POST https://raspberrypi/Safe_and_Rescue_Monitoring_Website/Sens_to_Data.php HTTP/1.1
#             # content-type: application/json
#             #
#             # Detect=upload&Detect_Time="Tue Apr  5 09:27:10 2022"&Detect_Result="[1, 0, 0, 0, 0, 0, 0, 0, 0, 0]"&Lat=2.332226&Long=99.0607&AOA=18.0

#             url = 'https://raspberrypi/Safe_and_Rescue_Monitoring_Website/Sens_to_Data.php'
#             detectionData = f'Detect=upload&Detect_Time={timeDetected}&Detect_Result=\"{detectionResult}\"&Lat={lat}&Long={lng}&AOA={AoA}'
#             x = requests.post(
#                 url, 
#                 headers={"content-type": "application/x-www-form-urlencoded"}, 
#                 data=detectionData,
#                 verify=False
#             )

#             line_count += 1
#         print(f'Processed {line_count} lines.')

# print(calc_victim_pos(pointsPos, AoAs))