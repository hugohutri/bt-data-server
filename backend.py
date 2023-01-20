#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import json
import time
from datetime import datetime
import asyncio
import math

import pickledb
db = pickledb.load('kandi.db', True)

devices = []


def get_time():
    return round(time.time() * 1000)


live = True
# start_time = "12.04.2021 19:20:22"
start_time = "18.04.2021 15:01:00"
date_time_obj = datetime.strptime(start_time, "%d.%m.%Y %H:%M:%S")
time_started = get_time()
room_state = {
    "devices": [],
    "updated": 0,
}
global devices_string
devices_string = []


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        if not live:
            update_room_state_from_db()
            if (devices_string):
                print("Sending db devices:")
                print(devices_string[0])
                print("SEND")
                self.wfile.write(devices_string[0].encode())
            return
        print("Sending roomstate: ", room_state["updated"])
        print("Sending devices: ", room_state["devices"])
        self.wfile.write(json.dumps(room_state).encode())
        return

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        data = self.rfile.read(int(self.headers['Content-Length']))
        json_data = json.loads(data)
        # devices.append(json_data)
        update_room_state(json_data)
        print(room_state)
        return


def rssi_to_meters(rssi: int, mode: str) -> int:

    if mode == "br":
        N = 2.4  # 3.5  # Environmental factor. Range 2-4
        power = -49  # Power estimation
        return 10**((power-rssi)/(10*N))

    else:
        N = 3  # 3.5  # Environmental factor. Range 2-4
        power = -45  # Power estimation
        return 10**((power-rssi)/(10*N))


def min_positive(values):
    return min([n for n in values if n > 0])


def find_next_key(numbers, current: int):
    return (min([n for n in numbers if (float(n) > current)]))


def update_room_state_from_db():
    # Get all timestamps from database
    global time_started
    keys = list(db.getall())
    current_time = float(room_state["updated"] or date_time_obj.timestamp())
    # next_time = math.inf
    # for key in keys:
    #     if float(key) > float(time):
    #         if float(key) < float(next_time):
    #             next_time = key
    next_key = find_next_key(keys, current_time)
    next_time = float(next_key)
    print("next_time", next_time)
    print("curr_time", current_time)
    cycle_seconds = next_time-current_time
    print("Cycle seconds:", cycle_seconds)
    # seconds_to_next = (float(next_time) -
    #                    float(time))
    # print("Seconds to next", seconds_to_next)

    # How long this program has ran
    elapsed_time = float(get_time() - time_started)/1000
    print("Elapsed: ", elapsed_time)

    seconds_to_next = float(next_time) - \
        (float(current_time)+float(elapsed_time))
    print("Seconds to next:", seconds_to_next)

    # print(elapsed_time, ">", cycle_seconds, "=", elapsed_time > cycle_seconds)
    if elapsed_time > cycle_seconds:
        time_started = get_time()
        print("Updating the room state!")
        data = str(db.get(next_key))
        print("Devices:", data)

        # for dev in list(data["devices"]):
        #     print(dev["addr"])
        devices_string = []
        devices_string.clear()
        devices_string.append(data)
    print()


def update_room_state(data):
    room_state["devices"] = []
    room_state["updated"] = get_time()
    for signal in data:

        if not "addr" in signal:
            continue

        device_type = ""
        if "major_device_class" in signal:
            device_type = signal["major_device_class"]

        mode = "le"
        if "mode" in signal:
            mode = signal["mode"]

        distance = -1
        rssi = 0
        if "rssi" in signal:
            rssi_str = signal["rssi"].split(" ")[0]
            rssi = int(rssi_str)
            distance = rssi_to_meters(rssi, mode)

        company = ""
        if "company" in signal:
            company = signal["company"]

        name = ""
        if "complete_local_name" in signal:
            name = signal["complete_local_name"]

        device = {
            "addr": signal["addr"],
            "distance": distance,
            "rssi": rssi,
            "name": name,
            "company": company,
            "device_type": device_type,
            "mode": mode
        }
        print("Device:", device)
        print()
        room_state["devices"].append(device)
    save_to_db(room_state)


def save_to_db(room_state):
    key = str(int(time.time()))
    db.set(key, json.dumps(room_state))
    print("Saved to the database")


async def start_server():
    server = HTTPServer(('localhost', 8000), RequestHandler)
    print('Starting server at http://localhost:8000')
    server.serve_forever()


# async def serve_from_db():
#     if not start_time:
#         print("Serving from the sensor")
#         return
#     print("Serving from the database")
#     keys = db.getall()
#     await asyncio.sleep(1)
#     print("WAITED")
#     for key in keys:
#         print(".:..................")
#         await asyncio.sleep(1)


async def main():
    keys = db.getall()
    print(date_time_obj.timestamp())
    print("KEYS: ", len(keys))
    # db_task = asyncio.create_task(serve_from_db())
    server_task = asyncio.create_task(start_server())
    # await db_task
    await server_task


if __name__ == '__main__':
    asyncio.run(main())
