import os
import piexif
from fractions import Fraction
import datetime

def to_deg(value, loc):
    """convert decimal coordinates into degrees, munutes and seconds tuple
    Keyword arguments: value is float gps-value, loc is direction list ["S", "N"] or ["W", "E"]
    return: tuple like (25, 13, 48.343 ,'N')
    """
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg =  int(abs_value)
    t1 = (abs_value-deg)*60
    min = int(t1)
    sec = round((t1 - min)* 60, 5)
    return (deg, min, sec, loc_value)


def change_to_rational(number):
    """convert a number to rantional
    Keyword arguments: number
    return: tuple like (1, 2), (numerator, denominator)
    """
    f = Fraction(str(number))
    return (f.numerator, f.denominator)


def set_gps_location(file_name, lat, lng, altitude):
    """Adds GPS position as EXIF metadata
    Keyword arguments:
    file_name -- image file
    lat -- latitude (as float)
    lng -- longitude (as float)
    altitude -- altitude (as float)
    """
    lat_deg = to_deg(lat, ["S", "N"])
    lng_deg = to_deg(lng, ["W", "E"])

    exiv_lat = (change_to_rational(lat_deg[0]), change_to_rational(lat_deg[1]), change_to_rational(lat_deg[2]))
    exiv_lng = (change_to_rational(lng_deg[0]), change_to_rational(lng_deg[1]), change_to_rational(lng_deg[2]))

    gps_ifd = {
        piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
        piexif.GPSIFD.GPSAltitudeRef: 1,
        piexif.GPSIFD.GPSAltitude: change_to_rational(round(altitude)),
        piexif.GPSIFD.GPSLatitudeRef: lat_deg[3],
        piexif.GPSIFD.GPSLatitude: exiv_lat,
        piexif.GPSIFD.GPSLongitudeRef: lng_deg[3],
        piexif.GPSIFD.GPSLongitude: exiv_lng,
    }

    exif_dict = {"GPS": gps_ifd}
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, file_name)

def insert_date(filename, date):

    exif_dict = {'Exif': {piexif.ExifIFD.DateTimeOriginal: date}}
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, filename)
    print 'insert'


def main():
    fotolog = r'C:\Users\cyh\Desktop\test\shp\matcher.txt'
    project_dir = os.path.dirname(fotolog)
    png_dir = project_dir + '/jpg'
    with open(fotolog, 'r') as log:
        log.readline()
        for y in log:
            data = y.split(',')
            weg_num, frame, Lat, Lon = data[0], data[2], float(data[4]), float(data[5])
            month = weg_num.split('_')[0][:2]
            day = weg_num.split('_')[0][2:]
            time = data[6]
            date = '2019:{}:{} {}'.format(month,day,time)
            jpgname = '{}/{}-{}.jpg'.format(png_dir, weg_num, frame)
            try:
                set_gps_location(jpgname, Lat, Lon, 0)
                insert_date(jpgname, date)
            except IOError:
                print jpgname + ' not found'
                continue
            finally:
                pass
    print 'tagged'
if __name__ == '__main__':
    fotolog = r'C:\Users\cyh\Desktop\test\shp\matcher.txt'
    project_dir = os.path.dirname(os.path.dirname(fotolog))
    png_dir = project_dir + '/jpg'
    with open(fotolog, 'r') as log:
        log.readline()
        for y in log:
            data = y.split(',')
            print y
            weg_num, frame, Lat, Lon = data[0], data[2], float(data[4]), float(data[5])
            month = weg_num.split('_')[0][:2]
            day = weg_num.split('_')[0][2:]
            time = data[6]
            date = '2019:{}:{} {}'.format(month,day,time)
            jpgname = '{}/{}-{}.jpg'.format(png_dir, weg_num, frame)
            try:
                insert_date(jpgname, date)
            except IOError:
                print jpgname + ' not found'
                continue
            finally:
                pass
    print 'tagged'