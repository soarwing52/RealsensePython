# PyRealsense for d435

in this project will have record bag and measure picture from bag

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

![](examples/google earth.PNG)


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

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc

