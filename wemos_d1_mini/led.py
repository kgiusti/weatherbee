#
# Licensed to the Apache Software Foundation (ASF) undeugr one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

from machine import Pin

class LED:
    def __init__(self, pin=2):
        self._pin = Pin(pin, Pin.OUT)
        self._state = "OFF"
        self.off()

    def on(self):
        self._pin.value(0)
        self._state = "ON"

    def off(self):
        self._pin.value(1)
        self._state = "OFF"

    @property
    def state(self):
        return self._state

def main():
    from time import sleep

    led = LED()
    for i in range(5):
        led.on()
        print("State=%s" % led.state)
        sleep(0.5)
        led.off()
        print("State=%s" % led.state)
        sleep(0.5)

