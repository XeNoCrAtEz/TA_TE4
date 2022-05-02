
from time import time, ctime
import csv
import requests

# GPS system object
GPSsys = GPS(isUsingMAVLink=False)

if GPSsys.GPSSamplingThread.is_alive(): print("\u001b[32mSuccess\u001b[0m")
else: raise RuntimeError("GPS sampling thread failed to run!")

csvUpdateTime = time() + 1
while True:
    lat, lng = GPSsys.get_lat_lng()

    if time() > csvUpdateTime:
        with open("data_gps.csv", mode='a') as resultFile:
            CSVWriter = csv.writer(resultFile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            CSVWriter.writerow([ctime(time()), lat, lng])
            csvUpdateTime = time() + 1
    print(lat, lng)

# NOTE: READ CSV FILE
csvFilename = 'data_gps.csv'
with open(csvFilename, 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter='\t')
    line_count = 0
    for row in csv_reader:
        timeDetected = row[0]
        lat = float(row[1])
        lng = float(row[2])
        print(f'At time {timeDetected}:')
        print(f'\tlat: {lat}  lng: {lng}')

        # POST https://raspberrypi/Safe_and_Rescue_Monitoring_Website/Sens_to_Data.php HTTP/1.1
        # content-type: application/json
        #
        # Detect=upload&Detect_Time="Tue Apr  5 09:27:10 2022"&Detect_Result="[1, 0, 0, 0, 0, 0, 0, 0, 0, 0]"&Lat=2.332226&Long=99.0607&AOA=18.0

        url = 'https://raspberrypi/Safe_and_Rescue_Monitoring_Website/Sens_to_Data.php'
        detectionData = f'Detect=upload&Detect_Time={timeDetected}&Detect_Result=\"{[0,0,0,0,0,0,0,0,0,0]}\"&Lat={lat}&Long={lng}&AOA={0}'
        x = requests.post(
            url, 
            headers={"content-type": "application/x-www-form-urlencoded"}, 
            data=detectionData,
            verify=False
        )

        line_count += 1
    print(f'Processed {line_count} lines.')