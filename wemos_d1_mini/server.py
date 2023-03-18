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

import json
import machine
import socket
import sys

import bme280
import led

led = led.LED()
_i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))
bme = bme280.BME280(i2c=_i2c)


def c_to_f(temp_c):
    return (temp_c * 1.8) + 32.0

def do_get(sock, target, in_file):
    global led
    global bme

    print("GET JSON")
    while True:
        line = in_file.readline().decode()
        if line == '':
            print("Client closed socket")
            return
        if line.strip() == "":
            # end of headers
            break;

    temp_c, hpa, hum_p = bme.raw_values

    out = json.dumps({'weatherbee':
                      {'F': c_to_f(temp_c),
                       'C': temp_c,
                       'hPa': hpa,
                       'H': hum_p,
                       "LED": led.state}}).encode()
    sock.sendall(b'HTTP/1.0 200 OK\r\n')
    sock.sendall(b'Content-type: application/json\r\n')
    sock.sendall(b'Content-length: %d\r\n\r\n' % len(out))
    sock.sendall(out)
    print("json sent %s" % out)

def do_put(sock, target, in_file):
    global led

    # skip headers
    while True:
        line = in_file.readline().decode()
        if line == '':
            print("Client closed socket")
            return
        if line.strip() == "":
            # end of headers
            break;
    print("READ BODY")
    line = in_file.readline().decode().strip()
    # expect json: {'weatherbee': {'led': 'on|off'}
    try:
        print("READ: %s" % line)
        data = json.loads(line)
        new_led = data['weatherbee']['led']
        print("NEW LED: %s" % new_led)
        if new_led.upper() == "ON":
            led.on()
        else:
            led.off()
        print("POST DONE OK")
        sock.sendall(b'HTTP/1.0 204 No Content\r\n\r\n')
    except Exception as exc:
        print("POST FAILED: %s" % exc)
        sock.sendall(b"HTTP/1.0 400 Bad Cheezeburger\r\n\r\n")
    print("PUT DONE")

def handle_client(client):
    client_file = client.makefile('rwb', 0)
    line = b''
    while True:
        line = client_file.readline().decode()
        if line == '':
            print("Client closed socket")
            return
        line = line.strip()
        if len(line) != 0:
            break

    print("REQUEST=%s" % line)
    request = line.split()
    method = request[0].upper()
    target = request[1].upper()
    if method == "GET":
        do_get(client, target, client_file)
    elif method == "PUT":
        do_put(client, target, client_file)
    else:
        client.sendall(b"HTTP/1.0 400 Bad Banana\r\n\r\n")

def run():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 8888))
    server.listen(5)
    print('listening on port 8888')

    while True:
        client, addr = server.accept()
        try:
            print('client connected from', addr)
            handle_client(client)
        except Exception as exc:
            print("Exception: %s" % exc)
        finally:
            client.close()

# run()
