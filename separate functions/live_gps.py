import serial
import datetime
from math import sin, cos, sqrt, atan2, radians

def gps_dis(location_1,location_2):
    R = 6373.0

    lat1 = radians(location_1[1])
    lon1 = radians(location_1[0])
    lat2 = radians(location_2[1])
    lon2 = radians(location_2[0])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    distance = distance*1000
    #print "Result:", distance
    return distance

def min2decimal(in_data):
    latgps = float(in_data)
    latdeg = int(latgps / 100)
    latmin = latgps - latdeg * 100
    lat = latdeg + (latmin / 60)
    return lat

def GPS():
    lon, lat = 0,0
    print('GPS start')
    serialPort = serial.Serial()
    serialPort.port = 'COM6'
    serialPort.baudrate = 4800
    serialPort.bytesize = serial.EIGHTBITS
    serialPort.parity = serial.PARITY_NONE
    serialPort.timeout = 2
    serialPort.open()
    first_location = [0, 0]
    try:
        while True:
            line = serialPort.readline()
            data = line.split(",")
            present = datetime.datetime.now()
            date = '{},{},{},{}'.format(present.day, present.month, present.year, present.time())
            if data[0] == '$GPRMC':
                if data[2] == "A":
                    lat = min2decimal(data[3])
                    lon = min2decimal(data[5])

                    current_location = [lon,lat ]
                    print 'gps ready, current location:{}'.format(current_location)
                    gps_dis(current_location,first_location)
                    first_location = current_location
            elif data[0] == '$GPGGA':
                if data[6] == '1':
                    lon = min2decimal(data[4])
                    lat = min2decimal(data[2])
                    current_location = [lon, lat]
                    print 'gps ready, current location:{}'.format(current_location)
                else:
                    print 'searching'
            """
            with open('./kml/live.kml', 'w') as pos:
                googleearth_message = '''<?xml version="1.0" encoding="UTF-8"?>
                  <kml xmlns="http://www.opengis.net/kml/2.2">
                    <Placemark>
                      <name>Live Point</name>
                      <description>hi im here</description>
                      <Point>
                        <coordinates>{},{},0</coordinates>
                      </Point>
                    </Placemark>
                  </kml>'''.format(lon, lat)
                pos.write(googleearth_message)
                """
    finally:

        print('GPS finish')

if __name__ == '__main__':
    GPS()
