This directory contains appropriate python validation for testing quality and accuracy of sensor.

This directory includes:
* the code.py file, for testing the sensors
* the lib/ folder and all of its contents (including subfolders and .mpy or .py files)
* any assets (such as images, sounds, etc.)

Here's the Raspberry Pi wired with I2C, below is an image diagram:
* Pi 3V to sensor VCC (red wire)
* Pi GND to sensor GND (black wire)
* Pi SCL to sensor SCL (yellow wire)
* Pi SDA to sensor SDA (blue wire)

![Wiring Diagram](https://cdn-learn.adafruit.com/assets/assets/000/083/290/medium640/sensors_cpy_rpi_BB_wiring.png?1572468047)

You must use the appropriate CircuitPython9 on your microcontroller. For Raspberry Pi 4, simply run the following command on your Raspberry Pi's terminal
```
pip3 install adafruit-circuitpython-mpu6050 --break-system-packages
```
Disclaimer:
* Please note, in order to instal the mentioned drivers on our Raspberry Pi, we had to utilize ```--break-system-packages``` in order to get the driver to install due to a ```python3-pip``` limitation on Raspberry Pi. Feel free to remove the mentioned line and see if it works; otherwise, proceed with caution and install at your own risk.
* We recommend using a fresh Raspberry Pi for aformentioned drivers, with sole usecase being dedicated to DUM-E and not repurposed for other taks.
