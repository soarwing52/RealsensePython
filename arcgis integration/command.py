import argparse
import class_measure


ap =  argparse.ArgumentParser()
ap.add_argument("-i","--id", required=False)

args = vars(ap.parse_args())

obj_id = args['id']

a = class_measure.Arc_Real(obj_id).video()

