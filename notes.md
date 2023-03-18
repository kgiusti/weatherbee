esptool.py --port /dev/ttyUSB0 --baud 1000000 write_flash --flash_size=4MB -fm dio 0 esp8266-1m-20220618-v1.19.1.bin

The filesystem starting at sector 153 with size 866 sectors looks corrupt.      
You may want to make a flash snapshot and try to recover it. Otherwise,         
format it with uos.VfsLfs2.mkfs(bdev), or completely erase the flash and        
reprogram MicroPython.

Fix:

>>> import uos
>>> uos.VfsLfs2.mkfs(bdev)

minicom -D /dev/ttyUSB0 -b115200

$ ls -l /dev/ttyUSB0
crw-rw----. 1 root dialout 188, 0 Mar 17 13:39 /dev/ttyUSB0

$ groups
kgiusti wheel dialout wireshark

ampy: Adafruit MicroPython Tool
-------------------------------

$ export AMPY_PORT=/dev/ttyUSB0
$ ampy ls
$ ampy put somefile.py  # write somefile.py to device
$ ampy rm somefile.py   # delete it

# copy server.py to device ram and execute it
$ ampy run --no-output wemos_d1_mini/server.py
$ ampy reset


Wireless AP
-----------

ESSID is "MicroPython-xxxxxx" where the x’s are the devices MAC address
MicroPython-6e47cc
micropythoN
IP address 192.168.4.1


On Board LED
------------

GPIO pin 2

>>> from machine import Pin
>>> p2 = Pin(2, Pin.OUT)
>>> p2.value(1)  # OFF
>>> p2.value(0)  # ON

