# Mirror PI - The mirror that's avoiding you

Run main code:

```
python3 faceReg.py
```

## Dependencies
Basic dependencies for Opencv
```
sudo apt-get install build-essential cmake pkg-config
sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng-dev
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get install libfontconfig1-dev libcairo2-dev
sudo apt-get install libgdk-pixbuf2.0-dev libpango1.0-dev
sudo apt-get install libgtk2.0-dev libgtk-3-dev
sudo apt-get install libhdf5-dev libhdf5-serial-dev libhdf5-103
sudo apt-get install libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5
sudo apt-get install python3-dev
```

Optimization libraries
```
sudo apt-get install libatlas-base-dev gfortran
```

Install opencv via pip 
```
sudo pip3 install opencv-contrib-python
```

These steps are a summary from this opencv installation [guide](https://www.pyimagesearch.com/2019/09/16/install-opencv-4-on-raspberry-pi-4-and-raspbian-buster/)

### Troubleshooting
* If you get this error ```undefined symbol: __atomic_fetch_add_8```  
    Run this command: ``` export LD_PRELOAD='/usr/lib/arm-linux-gnueabihf/libatomic.so.1' ``` 
    Or source the .env file included ``` source .env ```

## Camera
In order to activate the camera on the RPI, follow this [guide.](https://www.raspberrypi.org/documentation/configuration/camera.md)

Camera settings from [opencv.](https://stackoverflow.com/questions/11420748/setting-camera-parameters-in-opencv-python)

Camera settings for the raspberry built in programs [programs.](https://www.raspberrypi.org/documentation/raspbian/applications/camera.md)

https://www.pyimagesearch.com/2015/03/30/accessing-the-raspberry-pi-camera-with-opencv-and-python/

https://picamera.readthedocs.io/en/release-1.13/

Running a preview of the camera with the built-in Raspberry pi programs:

```raspivid -p 0,0,640,480 -t 0  ```

Best possible light through mirror I could find for now:

``` raspivid -p 0,0,640,480 -t 0 -fps 5 -ex night```

## GPIO
A summary of the GPIO library used can be found [here.](https://www.ics.com/blog/control-raspberry-pi-gpio-pins-python)
### Pinout map
Pinout map of the Raspberry Pi
```
   3V3  (1) (2)  5V    
 GPIO2  (3) (4)  5V    
 GPIO3  (5) (6)  GND   
 GPIO4  (7) (8)  GPIO14
   GND  (9) (10) GPIO15
GPIO17 (11) (12) GPIO18
GPIO27 (13) (14) GND   
GPIO22 (15) (16) GPIO23
   3V3 (17) (18) GPIO24
GPIO10 (19) (20) GND   
 GPIO9 (21) (22) GPIO25
GPIO11 (23) (24) GPIO8 
   GND (25) (26) GPIO7 
 GPIO0 (27) (28) GPIO1 
 GPIO5 (29) (30) GND   
 GPIO6 (31) (32) GPIO12
GPIO13 (33) (34) GND   
GPIO19 (35) (36) GPIO16
GPIO26 (37) (38) GPIO20
   GND (39) (40) GPIO21
```

### Connections
Table with the connections for the motors and switches
| Name          | Pin number | Color |
| ------------- |:----------:| -----:|
| direction  m1 |   3 	     | Green |
| step       m1 |   5  	     | Yellow|
| enable     m1 |   7 	     | White |
| switch_gnd m1 |   9        | Brown |
| switch     m1 |   11       | White |
| direction  m2 |   8        | Green |
| step       m2 |   10       | Yellow|
| enable     m2 |   12       | White |
| switch_gnd m2 |   14       | Brown |
| switch     m2 |   16       | White |

## TODO
* Handle when the mirror reachs end points
* Add logic for the second motor

 
