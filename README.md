WEMOS D1 LITE BMP280 Micropython Demo
=====================================

A little IoT demo that runs on an esp8266-based WEMOS D1 Lite board. A
BMP280 temperature/humidity/pressure sensor is attached to the I2C
bus. The WEMOS board is configured as a WiFi access port. Access to
the sensor is provided via a simple HTTP/1.0 interface.

Includes a command line tool (weatherbee) that can be used to
communicate with the board over WiFi.

