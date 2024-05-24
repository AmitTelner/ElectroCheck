import socket
import sqlite3

from device import *
import pickle
import threading
import rsa

class user:
    def __init__(self, userclient: socket.socket):
        self.userclient = userclient

    def getdata(self, d: elecdevice):
        self.userclient.send(pickle.dumps((d.name, d.readings)))

    def handle_client(self, c: socket.socket, password: str, privkey: rsa.PrivateKey, lock: threading.Lock,
                      clients: list[socket.socket]):
        try:
            while c not in clients:
                message = rsa.decrypt(c.recv(1024), privkey).decode()
                if password == message and c not in clients:
                    lock.acquire()
                    clients.append(c)
                    lock.release()
                    print("new client")
                    print(clients)
                    c.send("welcome".encode())
                else:
                    c.send("wrong password".encode())
        except:
            print("failed")

class admin(user):
    def addplug(self, d: elecdevice, devices: dict, curr: sqlite3.Cursor):
        devices = devices | {d.name: d}
        instructionstart = "INSERT INTO plugs(device_id,name,current_ip,mac_address,device_key, readings) \nVALUES( "
        curr.execute(
            instructionstart + "\'" + str(d.id) + "\'" + ", " + "\"" + d.name + "\"" + ", " + "\"" + d.ip
                 + "\"" + ", " + "\"" + str(d.mac) + "\"" + ", " + "\"" + str(
                d.key) + "\", \"" + "{}" + "\");")