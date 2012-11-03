ram
===
ram is a command line asset manager focused on simplifying iOS and Android
development. More information is available at
https://github.com/spennington/ram

ram is licensed under the Apache Licence, Version 2.0
(http://www.apache.org/licenses/LICENSE-2.0.html).

Installation
------------
ram relies on the ImageMagick project for image manipulation. So, the first
step is to install ImageMagick (http://www.imagemagick.org/script/index.php)

Download and install the latest release:

    curl -O http://cloud.github.com/downloads/spennington/ram/ram-0.1.0.tar.gz 
    tar -xzvf ram-0.1.0.tar.gz
    cd ram-0.1.0
    sudo python setup.py install

How it works
------------
ram manages image assets by generating different versions of the asset from a
master file. This is best demonstrated with an example.

Consider an Android project with a directory structure something like:

    AndroidProject
                 |
                 |---->src/
                 |---->res
                         |
                         |----->drawable-ldpi
                         |                  |
                         |                  |--->ic_launcher.png
                         |                  |--->image.png
                         |
                         |----->drawable-mdpi
                         |                  |
                         |                  |--->ic_launcher.png
                         |                  |--->image.png
                         |----->drawable-hdpi
                         |                  |
                         |                  |--->ic_launcher.png
                         |                  |--->image.png
                         |----->drawable-xhdpi
                         |                  |
                         |                  |--->ic_launcher.png
                         |                  |--->image.png

As you can there are two image assets but each must be replicated and resized
for each of the different target densitites.

If these images were to change it would require exporting of eight new images
by a designer and the developer would need to replace eight new images inside
the project.

ram allows the designer to export a single high resolution asset and allows the
developer to create generation rules for converting that asset to the necessary
resolution.

So, a ram manged project directory structure might look something like:

    AndroidProject
                 |---->ramfile.json
                 |---->src/
                 |---->masters/
                              |---->ic_launcher.psd
                              |---->image.psd
                 |---->res/
                         |----->drawable-ldpi
                         |----->drawable-mdpi
                         |----->drawable-hdpi
                         |----->drawable-xhdpi

In the ram managed project the developer has created a masters directory which
contains all the high resolution images that actual assets will be generated
from.

Next the developer sets up the ram conversions:

    ram init
    ram add masters/*

This will initialize a ram managed folder and then mark the two master files as
ready for conversion.

The developer could now execute:

    ram status

Which will inform the developer that the two master files are ready for
conversion.

Next, the developer must create a ramfile (ramfile.json) which instructs ram
how to convert the master images. An example ram file might look something
like:

    {
        "templates": {
            "android": {
                "slaves": [
                    {
                        "path": "res/drawable-ldpi/{name}",
                        "width": "{basewidth} * 0.75",
                        "height": "{baseheight} * 0.75"
                    },
                    {
                        "path": "res/drawable-mdpi/{name}",
                        "width": "{basewidth}",
                        "height": "{baseheight}"
                    },
                    {
                        "path": "res/drawable-hdpi/{name}",
                        "width": "{basewidth} * 1.5",
                        "height": "{baseheight} * 1.5"
                    },
                    {
                        "path": "res/drawable-xhdpi/{name}",
                        "width": "{basewidth} * 2",
                        "height": "{baseheight} * 2"
                    }
                ]
            }
        },
       "conversions": [
          {
             "master":"masters/ic_launcher.psd",
             "template": "android",
             "name": "ic_launcher.png",
             "basewidth": 48,
             "baseheight": 48
          },
          {
            "master":"masters/image.psd",
             "template": "android",
             "name": "image.png",
             "basewidth": 200,
             "baseheight": 100
          }
       ]
    }


At a high level the ramfile lists two conversions, one for
masters/ic_launcher.png and one for masters/image.png. The files are then
converted using the 3:4:6:8 conversion paradigm used by Android
(http://developer.android.com/guide/practices/screens_support.html#DesigningResources)

Finally, the developer can execute:

    ram convert

And ram will convert the two master files into eight image files inside the
correct folders.

ramfile
-------

The ramfile.json is a json file which provides a conversion strategy for ram.

Example file with two useful profiles: ios and android.

    {
        "templates": {
            "android": {
                "slaves": [
                    {
                        "path": "testfiles/res/drawable-ldpi/{name}",
                        "width": "{basewidth} * 0.75",
                        "height": "{baseheight} * 0.75"
                    },
                    {
                        "path": "testfiles/res/drawable-mdpi/{name}",
                        "width": "{basewidth}",
                        "height": "{baseheight}"
                    },
                    {
                        "path": "testfiles/res/drawable-hdpi/{name}",
                        "width": "{basewidth} * 1.5",
                        "height": "{baseheight} * 1.5"
                    },
                    {
                        "path": "testfiles/res/drawable-xhdpi/{name}",
                        "width": "{basewidth} * 2",
                        "height": "{baseheight} * 2"
                    }
                ]
            },
            "ios": {
                "slaves": [
                    {
                        "path": "{root}/{name}{extension}",
                        "width": "{basewidth}",
                        "height": "{baseheight}"
                    },
                    {
                        "path": "{root}/{name}@2x{extension}",
                        "width": "{basewidth} * 2.00",
                        "height": "{baseheight} * 2.00"
                    }
                ]
            }
        },
       "conversions": [
          {
             "master":"testfiles/android.png",
             "template": "android",
             "name": "android.png",
             "basewidth": 100,
             "baseheight": 100
          },
          {
             "master":"testfiles/ios.png",
             "template": "ios",
             "root": "testfiles/ios",
             "name": "ios",
             "extension": ".png",
             "basewidth": 100,
             "baseheight": 100
          },
          {
             "master":"testfiles/file.png",
             "slaves":[
                {
                   "path":"testfiles/res/drawable-ldpi/image.png",
                   "width":75,
                   "height":75
                },
                {
                   "path":"testfiles/res/drawable-mdpi/image.png",
                   "width":100,
                   "height":100
                },
                {
                   "path":"testfiles/res/drawable-hdpi/image.png",
                   "width":150,
                   "height":150
                },
                {
                   "path":"testfiles/res/drawable-xhdpi/image.png",
                   "width":200,
                   "height":200
                }
             ]
          }
       ]
    }
    
Usage
-----

ram attemtps to create a command line interface inspired by git so the learning
curve is hopefully low. (Assuming you already are comfortable with git)

See `ram -h`

