import argparse
import class_measure


ap =  argparse.ArgumentParser()
ap.add_argument("-p","--path", required=False)

args = vars(ap.parse_args())

jpg_path = args['path']

a = class_measure.Arc_Real(jpg_path).video()

