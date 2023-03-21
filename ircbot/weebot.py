#!/usr/bin/python

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
import socket
import sys

# pip install irc
from irc.bot import SingleServerIRCBot


# import logging
# logging.basicConfig(level=logging.DEBUG)

class WeeBot(SingleServerIRCBot):
    def __init__(self, host, port, channel, nick,
                 server_addr="192.168.4.1:8888"):
        super().__init__([(host, port)], nick, nick)

        self.channel = channel
        self.nick = nick

        host, port = server_addr.split(":")
        self.server_addr = (host, int(port))

    def on_welcome(self, conn, event):
        print(f"Event: {event}")
        conn.join(self.channel)

    def on_privmsg(self, conn, event):
        print(f"Privmsg Event: {event}")

    def on_pubmsg(self, conn, event):
        print(f"Pubmsg Event: {event}")
        text = event.arguments[0]
        if text.startswith(self.nick + ":") or text.startswith(self.nick + ","):
            self.handle_command(conn, event)

    def error_reply(self, conn, nick, msg):
        usage = "Usage: 'GET' or 'LED ON' or 'LED OFF'"
        conn.privmsg(self.channel, f"{nick}: {msg}")
        conn.privmsg(self.channel, f"{nick}: {usage}")

    def handle_command(self, conn, event):
        text = event.arguments[0][len(self.nick) + 1:]
        command = text.strip().upper().split()

        try:
            if command[0] == "GET":
                self.handle_get(conn, event.source.nick)
            elif command[0] == "LED":
                self.handle_led(conn, event.source.nick, command[1])
            else:
                self.error_reply(conn, event.source.nick, f"unrecognized command: '{text}'")
        except Exception as exc:
            self.error_reply(conn, event.source.nick, "Oops! Try again!")
            print(f"Ouch! falure: {exc}")

        # conn.privmsg(self.channel, f"{event.source.nick}, {text.lstrip().upper()}")
        # input: "kgiusti: weebot: Test1 Test2 Test3"
        # output: "weebot: kgiusti, TEST1 TEST2 Test3"

    def handle_get(self, conn, nick):
        # get current sensor data
        #
        with socket.create_connection(self.server_addr, timeout=10) as client:
            client.sendall(b"GET /weatherbee HTTP/1.0\r\n\r\n")

            # strip headers
            in_file = client.makefile('rwb', 0)
            while True:
                line = in_file.readline().decode()
                if line == '':
                    self.error_reply(conn, nick, "Ouch: connection failed!")
                    return
                if  line.strip() == '':
                    break;

            line = in_file.readline().decode().strip()
            data = json.loads(line)["weatherbee"]

            temp_c = data['C']
            temp_f = data['F']
            hum = data['H']
            pres = data['hPa']
            state = data['LED']

            response = f"{temp_c}C {temp_f}F {hum}% {pres}hPa (LED is {state})"
            conn.privmsg(self.channel, f"{nick}: {response}")

    def handle_led(self, conn, nick, new_value):
        # set the board led on or off
        #
        if new_value not in ["ON", "OFF"]:
            self.error_reply(conn, nick, f"Invalid LED state: {new_value}")
            return

        with socket.create_connection(self.server_addr, timeout=10) as client:
            data = json.dumps({'weatherbee': {'led': new_value}}).encode()
            client.sendall(b"PUT /weatherbee/led HTTP/1.0\r\n")
            client.sendall(b"Content-Type: application/json\r\n")
            cl = "Content-Length: %s\r\n" % (len(data) + 2)
            client.sendall(cl.encode())
            client.sendall(b"\r\n")
            client.sendall(data)
            client.sendall(b'\r\n')

            client_file = client.makefile('rwb', 0)
            response = client_file.readline().decode()
            if '204' not in response:
                self.error_reply(conn, nick, f"server error: {response}")
            else:
                conn.privmsg(self.channel, f"{nick}: LED state set to {new_value}")


def main():
    try:
        address, channel = sys.argv[1:3]
    except ValueError:
        exit("Usage: weebot.py IRC-HOST[:PORT] CHANNEL [NICK]")

    try:
        nick = sys.argv[3]
    except IndexError:
        nick = "weebot"

    try:
        host, port = address.split(":", 1)
    except ValueError:
        host, port = address, 6667

    port = int(port)

    WeeBot(host, port, channel, nick).start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
