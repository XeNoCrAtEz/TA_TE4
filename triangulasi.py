import subprocess
import csv
import datetime
from functions import *
import requests

for i in range(3):
    print(f"Sampling point-{i}")
    subprocess.call(['python', 'samplePoint.py', str(i)])
    print("\n")

posList = []
AoAList = []
for i in range(3):
    csvFilename = 'detection_results/result' + str(i) + '.csv'
    with open(csvFilename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        line_count = 0
        for row in csv_reader:
            timeDetected = row[0]
            detectionResult = row[1]
            lat = float(row[2])
            lng = float(row[3])
            AoA = float(row[4])
            print(f'At time {timeDetected}:')
            print(f'\tDetection result: {detectionResult}')
            print(f'\tlat: {lat}  lng: {lng}')
            print(f'\tAoA: {AoA}')

            posList.append([lat, lng])
            AoAList.append(AoA)

            # POST https://raspberrypi/Safe_and_Rescue_Monitoring_Website/Sens_to_Data.php HTTP/1.1
            # content-type: application/json
            #
            # Detect=upload&Detect_Time="Tue Apr  5 09:27:10 2022"&Detect_Result="[1, 0, 0, 0, 0, 0, 0, 0, 0, 0]"&Lat=2.332226&Long=99.0607&AOA=18.0

            url = 'https://raspberrypi/Safe_and_Rescue_Monitoring_Website/Sens_to_Data.php'
            detectionData = f'Detect=upload&Detect_Time={timeDetected}&Detect_Result=\"{detectionResult}\"&Lat={lat}&Long={lng}&AOA={AoA}'
            x = requests.post(
                url, 
                headers={"content-type": "application/x-www-form-urlencoded"}, 
                data=detectionData,
                verify=False
            )

            line_count += 1
        print(f'Processed {line_count} lines.')

print(calc_victim_pos(posList, AoAList))