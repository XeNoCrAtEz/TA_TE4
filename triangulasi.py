import subprocess
import csv
import datetime
from utils import *
import requests
from detectionData import *

# pirSums = {}
# pirNums = {}
# AoAs = {}
# pointsPos = {
#     # 1: (0, 0),
#     # 2: (5, 0),
#     # 3: (10, 0),
#     # 4: (15, 0),
#     # 5: (17.5, -4.3),
#     # 6: (12.5, -4.3),
#     # 7: (7.5, -4.3),
#     # 8: (2.5, -4.3),
#     # 9: (0, -8.6),
#     # 10: (5, -8.6),
#     # 11: (10, -8.6),
#     # 12: (15, -8.6)
# }

# i = 1
# with open(f'Point{i}_5m.csv') as dataFile:
#     dataFileReader = csv.reader(dataFile, delimiter=',')
#     pirSums[i] = [0 for _ in range(10)]
#     pointsPos[i] = [0,0]
#     line_count = 0
#     # jumlahkan smua pendeteksian
#     for row in dataFileReader:
#         if float(row[11]) != 0.0: pointsPos[i][0] += float(row[11])
#         if float(row[12]) != 0.0: pointsPos[i][1] += float(row[12])
#         for j in range(len(pirSums[i])):
#             pirSums[i][j] += int(row[j+1])
#         line_count += 1
#     pointsPos[i][0] /= line_count
#     pointsPos[i][1] /= line_count
    
#     # cari nomor pir yg mendeteksi
#     maxIdx = pirSums[i].index(max(pirSums[i]))
#     pirNums[i] = [maxIdx-1, maxIdx, (maxIdx+1)%10]
#     # hitung AoA
#     maxIdxValue = [pirSums[i][pirNum] for pirNum in pirNums[i]]
#     AoAs[i] = calc_AoA(maxIdxValue, pirNums[i])

#     print(f"Titik{i}:")
#     print(f"    PIRSums: {pirSums[i]}")
#     print(f"    PIR:     {[pirNums[i][j]+1 for j in range(3)]}")
#     print(f"    AoA:     {AoAs[i]}")
#     print(f"    Posisi:  {pointsPos[i]}")

# for i in range(4, 7):
#     with open(f'Point{i}_5m.csv') as dataFile:
#         dataFileReader = csv.reader(dataFile, delimiter=',')
#         pirSums[i] = [0 for _ in range(10)]
#         pointsPos[i] = [0,0]
#         line_count = 0
#         # jumlahkan smua pendeteksian
#         for row in dataFileReader:
#             if float(row[11]) != 0.0: pointsPos[i][0] += float(row[11])
#             if float(row[12]) != 0.0: pointsPos[i][1] += float(row[12])
#             for j in range(len(pirSums[i])):
#                 pirSums[i][j] += int(row[j+1])
#             line_count += 1
#         pointsPos[i][0] /= line_count
#         pointsPos[i][1] /= line_count
#         pointsPos[i][0], pointsPos[i][1] = latlngToXY(
#             pointsPos[1][0], pointsPos[1][1],
#             pointsPos[i][0], pointsPos[i][1]
#         )
#         # cari nomor pir yg mendeteksi
#         maxIdx = pirSums[i].index(max(pirSums[i]))
#         pirNums[i] = [maxIdx-1, maxIdx, (maxIdx+1)%10]
#         # hitung AoA
#         maxIdxValue = [pirSums[i][pirNum] for pirNum in pirNums[i]]
#         AoAs[i] = calc_AoA(maxIdxValue, pirNums[i])

#         print(f"Titik{i}:")
#         print(f"    PIRSums: {pirSums[i]}")
#         print(f"    PIR:     {[pirNums[i][j]+1 for j in range(3)]}")
#         print(f"    AoA:     {AoAs[i]}")
#         print(f"    Posisi:  {pointsPos[i]}")

originData = DetectionDataReader(f"Point1_5m.csv", ',')
originData.relativePos = originData.globalPos.to_relative(originData.globalPos)
print(originData)
detectionData = [DetectionDataReader(f"Point{i}_5m.csv", ',') for i in range(8, 11)]
for data in detectionData:
    data.relativePos = data.globalPos.to_relative(originData.globalPos)
    print(data)

tmpA = []
tmpb = []
for data in detectionData:
    x_i, y_i = data.relativePos.x, data.relativePos.y
    a_i = to_rad(data.AoA)
    tan_a = np.tan(a_i)
    tmpA.append([-tan_a, 1])
    tmpb.append([y_i - x_i*tan_a])
A = np.array(tmpA)
# A = np.array(
#     [[-tan(a1), 1],
#      [-tan(a2), 1],
#      [-tan(a3), 1]]
# )
b = np.array(tmpb)
# b = np.array(
#     [[y1-x1*tan(a1)],
#      [y2-x2*tan(a2)],
#      [y3-x3*tan(a3)]]
# )

print("")
print(f"A:")
print(f"{A}")
print(f"b:")
print(f"{b}")

# c = ( (A' * A)^-1 * A' * b )'
targetPos = np.transpose(np.linalg.inv(np.transpose(A).dot(A)).dot(np.transpose(A)).dot(b) ).tolist()[0]

# realTargetPos = (15, -1.5)
print("")
# print(f"Real Target Pos =       {realTargetPos}")
print(f"Calculated Target Pos = {RelativeCoord(originData.globalPos, targetPos[0], targetPos[1]).to_global()}")

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