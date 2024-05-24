import sqlite3
import pickle
import json

class elecdevice:
    def __init__(self, id: str, key: str, ip: str, name: str, mac: str, readings: dict):
        self.id = id
        self.key = key
        self.ip = ip
        self.name = name
        self.mac = mac
        self.readings = readings

    def new_reading(self, time: str, reading: str, curr: sqlite3.Cursor):
        print(self.readings)
        print(self.id)
        self.readings = {str(time): reading} | self.readings
        print(f"""
        update plugs
        set readings = {json.dumps(str(self.readings))}
        where device_id = {str(self.id)};
        """)
        curr.execute(f"""
        update plugs
        set readings = {json.dumps(str(self.readings))}
        where device_id = \'{self.id}\';
        """)
