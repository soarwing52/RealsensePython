import argparse
import class_measure


ap =  argparse.ArgumentParser()
ap.add_argument("-n","--num", required=False,help='name of user')
ap.add_argument("-w","--wegid", required=True )
ap.add_argument("-p","--path",required=True)
ap.add_argument("-t", "--type", required=False)
args = vars(ap.parse_args())


bag = args['path']
weg_id = args['wegid']
num = args['num']
view_type = args['type']

a = class_measure.Arc_Real(bag,weg_id)

if view_type == 'V':
    a.video()
else:
    a.measure(num)