#! python3

# Copyright Tomer Figenblat.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Python script for discovering Switcher devices."""
import sqlite3
import tkinter as tk
import makedatabase
import time
import asyncio
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from dataclasses import asdict
from pprint import PrettyPrinter
from typing import List
import pickle
from device import elecdevice
import datetime
from aioswitcher.bridge import (
    SWITCHER_UDP_PORT_TYPE1,
    SWITCHER_UDP_PORT_TYPE1_NEW_VERSION,
    SWITCHER_UDP_PORT_TYPE2,
    SWITCHER_UDP_PORT_TYPE2_NEW_VERSION,
    SwitcherBridge,
)
from aioswitcher.device import DeviceType, SwitcherBase

printer = PrettyPrinter(indent=4)

_examples = (
    """Executing this script will print a serialized version of the discovered Switcher
devices broadcasting on the local network for 60 seconds.
You can change the delay by passing an int argument: discover_devices.py 30

Switcher devices uses two protocol types:
    Protocol type 1 (UDP port 20002 or 10002), used by: """
    + ", ".join(d.value for d in DeviceType if d.protocol_type == 1)
    + """
    Protocol type 2 (UDP port 20003 or 10003), used by: """
    + ", ".join(d.value for d in DeviceType if d.protocol_type == 2)
    + """
You can change the scanned protocol type by passing an int argument: discover_devices.py -t 1

Note:
    WILL PRINT PRIVATE INFO SUCH AS DEVICE ID AND MAC.

Example output:
    Switcher devices broadcast a status message every approximately 4 seconds. This
    script listens for these messages and prints a serialized version of the to the
    standard output, for example (note the ``device_id`` and ``mac_address`` properties)::
    ```
        {   'auto_shutdown': '03:00:00',
            'device_id': 'aaaaaa',
            'device_state': <DeviceState.OFF: ('0000', 'off')>,
            'device_type': <DeviceType.V2_ESP: ('Switcher V2 (esp)', 'a7', <DeviceCategory.WATER_HEATER: 1>)>,
            'electric_current': 0.0,
            'ip_address': '192.168.1.33',
            'last_data_update': datetime.datetime(2021, 6, 13, 11, 11, 44, 883003),
            'mac_address': '12:A1:A2:1A:BC:1A',
            'name': 'My Switcher Boiler',
            'power_consumption': 0,
            'remaining_time': '00:00:00'}
    ```
Print all protocol types devices for 30 seconds:
    python discover_devices.py 30 -t all\n

Print only protocol type 1 devices:
    python discover_devices.py -t 1\n

Print only protocol type 2 devices:
    python discover_devices.py -t 2\n
"""  # noqa E501
)

parser = ArgumentParser(
    description="Discover and print info of Switcher devices",
    epilog=_examples,
    formatter_class=RawDescriptionHelpFormatter,
)
parser.add_argument(
    "delay",
    help="number of seconds to run, defaults to 60",
    type=int,
    nargs="?",
    default=60,
)
possible_types = ["1", "2", "all"]
parser.add_argument(
    "-t",
    "--type",
    required=False,
    choices=possible_types,
    help=f"set protocol type: {possible_types}",
    type=str,
)


async def print_devices(delay: int, ports: List[int], ids: list[dict[str:str]], curr: sqlite3.Cursor, conn: sqlite3.Connection, devices: dict) -> None:
    pureids = []
    for i in devices:
        pureids.append(devices[i].id)
    """Run the Switcher bridge and register callback for discovered devices."""
    instructionstart = "INSERT INTO plugs(device_id,name,current_ip,mac_address,device_key, readings) \nVALUES( "
    def on_device_found_callback(device: SwitcherBase) -> None:
        """Use as a callback printing found devices."""
        d =asdict(device)
        isin = False
        print(d["device_id"])
        for i in devices:
            if d["device_id"] == devices[i].id:
                isin = True
        if isin:
            otherdevice= None
            for i in ids:

                if d["device_id"] == i["device_id"]:
                    otherdevice = i

            if otherdevice is not None and float(d["electric_current"]) != float(otherdevice["electric_current"]):
                otherdevice["electric_current"] = d["electric_current"]
                print(d["device_id"] + " updated")
            elif d["device_id"] in pureids and otherdevice is None:
                ids.append(d)
                print("updated")
            else: print("bees")
        else:
            print(instructionstart +"\"" + str(d["device_id"]) + "\"" + ", "+"\""+ d["name"] +"\""+", "+"\""+ d["ip_address"] + "\"" +", "+ "\"" + str(d["mac_address"]) + "\"" +", "+ "\"" +str(d["device_key"]) + "\", "+ str(pickle.dumps([])) +" );\"")
            curr.execute(instructionstart +"\"" + str(d["device_id"]) + "\"" + ", "+"\""+ d["name"] +"\""+", "+"\""+ d["ip_address"] + "\"" +", "+ "\"" + str(d["mac_address"]) + "\"" +", "+ "\"" +str(d["device_key"]) + "\", \""+ "{}" +"\");")
            conn.commit()
            ids.append(d)
            n = datetime.datetime.now()
            devices.update({d["name"]:elecdevice(d["device_id"],d["device_key"], d["ip_address"], d["name"], d["mac_address"], {n.strftime("%d/%m/%Y %H:%M:%S"): d["electric_current"]})})
            print(ids)
            pureids.append(d["device_id"])
            print("there are none like me")

    async with SwitcherBridge(on_device_found_callback, broadcast_ports=ports):
        await asyncio.sleep(delay)


def discoverdevices(ids: List[str], curr: sqlite3.Cursor, conn: sqlite3.Connection, devices: dict):
    args = parser.parse_args()

    if args.type == "1":
        ports = [SWITCHER_UDP_PORT_TYPE1, SWITCHER_UDP_PORT_TYPE1_NEW_VERSION]
    elif args.type == "2":
        ports = [SWITCHER_UDP_PORT_TYPE2, SWITCHER_UDP_PORT_TYPE2_NEW_VERSION]
    else:
        ports = [
            SWITCHER_UDP_PORT_TYPE1,
            SWITCHER_UDP_PORT_TYPE1_NEW_VERSION,
            SWITCHER_UDP_PORT_TYPE2,
            SWITCHER_UDP_PORT_TYPE2_NEW_VERSION,
        ]

    try:
        asyncio.run(print_devices(args.delay, ports, ids, curr, conn, devices))

    except KeyboardInterrupt:
        exit()
