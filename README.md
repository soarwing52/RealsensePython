# PyRealsense for d435

in this project will have record bag and measure picture from bag with the RealsenseD435 camera

## Getting Started

This is a project to get single frames from D435 and save a serie of frames in a bag
#the save_single_frame function can't get depth data, show always 0,0,0, therefore I can only use rs.recorder


### Prerequisites

What things you need to install the software and how to install them

```
pip install --upgrade pip
pip install --user pyrealsense2 
pip install --user opencv-python 
pip install --user argparse
pip install --user py-getch
```
### Data Preparation
use the data capture it will create 
bag files
foto_log
kml/ live position and photos

use the shp& png to create shp and png


the output will be ready for Arcgis


### Installing

A step by step series of examples that tell you how to get a development env running

After installed, copy widgets2 into Lib/matplotlib
and copy def_measure to C:\Users\yourusername\AppData\Roaming\Python\Python27\site-packages



### Data Capture

the data capture script will automatically generate three folders: bag, foto_log, and kml

it will put the recorded bag in bag format, 

information of index,color frame number, depth frame number, longtitude, lattitude, day, month, year, timewill be saved in txt format in foto_log

kml will generate live location as live, and the location with recorded places in Foto.kml
use Google Earth: Temporary Places/Add/Networklink link to folder/kml/ live for location Foto.kml for foto point

![g earth](https://github.com/soarwing52/RealsensePython/blob/master/examples/google%20earth.PNG?raw=true)

### Data process

to prepare the data, use the data_prepare.py
first generate jpg, the pipeline sometimes drop frames, I made it loop two times, to besafe can be run more times
then prepare list, it will first generate framelist of color and depth with timestampe, then match timestamp within 25ms
then it will match the frame number from the foto_log file to get the gps information.
Because the latency cause for example: in log is frame no.100 but it could happen that the recorded is 99-102, so I match within a range of +-5, though currently it will have multiple points, not resolved yet.
and then can generate shp for arcgis, and also geotag the generated photos

### in ArcGIS

in Arcgis use hyperlink and show script
put in 

```
import subprocess
def OpenLink ( [weg_num]  , [png_path] ):
  bag = [png_path] 
  weg_id = [weg_num] 
  comnd = 'python videoclass.py -w {} -p {}'.format(weg_id,bag)
  subprocess.call(comnd)
  return
```
or
```
import subprocess
def OpenLink ( [weg_num] , [foto_id]  , [png_path] ):
  bag = [png_path] 
  weg_id = [weg_num] 
  c_f_n= str( [foto_id]  )
  comnd = 'python measure.py -n {} -w {} -p {}'.format(c_f_n,weg_id,bag)
  subprocess.call(comnd)
  return
```
End with an example of getting some data out of the system or using it for a little demo

in here we use subprocess because the current realsense library will freeze after set_real_time(False)
and ArcMap don't support multithread nor multicore
therefore we can't use the simple import but have to call out command line and then run python

## Authors

* **Che-Yi Hung** - *Initial work* - [soarwing52](https://github.com/soarwing52)

