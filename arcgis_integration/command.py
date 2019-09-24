import argparse
import class_measure
import os

ap = argparse.ArgumentParser()
ap.add_argument("-p","--path", required=False)

args = vars(ap.parse_args())

jpg_path = args['path']

if '0520' in jpg_path or 'Kamera' in jpg_path:
    os.startfile(jpg_path)
else:
    class_measure.Arc_Real(jpg_path)

