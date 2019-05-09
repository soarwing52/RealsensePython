import argparse
import class_measure

ap =  argparse.ArgumentParser()
ap.add_argument("-n","--num", required=True,help='name of user')
ap.add_argument("-w","--wegid", required=True )
ap.add_argument("-p","--path",required=True)
args = vars(ap.parse_args())

#print args['num']
#print args['wegid']
#print args['path']
bag = args['path']
weg_id = args['wegid']
num = args['num']

a = class_measure.Arc_Real(bag,weg_id)
a.measure(num)
raw_input('go')
