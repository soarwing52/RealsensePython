# PyRealsense for d435

in this project will have record bag and measure picture from bag

## Getting Started

functions:
q for leave
h for last/j for next /u for search frame


### Prerequisites

What things you need to install the software and how to install them

```
pip install --upgrade pip
pip install --user pyrealsense2 
pip install --user opencv-python 
```

### Installing

A step by step series of examples that tell you how to get a development env running

After installed, copy widgets2 into Lib/matplotlib
and copy def_measure to C:\Users\yourusername\AppData\Roaming\Python\Python27\site-packages

```

```

in Arcgis use hyperlink and show script
put in 

```
import def_measure
def OpenLink ( [Str_ID] , [bagpath] , [Color_text]):
  bag_path = [bagpath] 
  weg_id = [Str_ID]
  color_id = [Color_text] 
  def_measure.frame_match(bag_path,weg_id,color_id)
  return
```
or
```
import def_measure
def OpenLink ( [path2]  , [Path]  ):
  bag_path = [Path] 
  weg_id = [path2] 
  def_measure.video(bag_path,weg_id)
  return
```
End with an example of getting some data out of the system or using it for a little demo

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

