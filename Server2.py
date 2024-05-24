import socket
import select
import time
import threading
import queries
import sqlite3
import pickle
import device
import datetime
import rsa
import json
from user import *
import hashlib

def handle_client(c: socket.socket, privkey: rsa.PrivateKey, lock:threading.Lock, clients: list, conn = sqlite3.Connection):
    curr = conn.cursor()
    curr.execute("select * from users")
    passwords = curr.fetchall()
    usernames = []
    for i in passwords:
        usernames.append(i[0])
    try:
        while c not in clients:
            message = rsa.decrypt(c.recv(1024), privkey).decode()
            m = message.split(",")
            hashes = []
            for i in m:
                hashes.append(hash(i))
            if hashes[0] in usernames and c not in clients:
                lock.acquire()
                print("gotten past first check")
                for i in passwords:
                    if i[0] == hashes[0] and i[1] == hashes[1]:
                        if i[2] == 1:
                            clients.append(admin(c))
                        else:
                            clients.append(user(c))
                lock.release()
                print("new client")
                print(clients)
                c.send("welcome".encode())
            else:
                c.send("wrong password".encode())

    except:
        print("failed")


def get(lock:threading.Lock, pubkey: rsa.PublicKey, privkey: rsa.PrivateKey, server: socket.socket, conn: sqlite3.Connection, clients: list):

    while True:
        rlist, wlist, xlist = select.select([server] + clients, clients, [])
        for client in rlist:  # if the client is new
            if client is server:
                try:
                    c, address = client.accept()
                    c.send(pickle.dumps(pubkey))
                    t = threading.Thread(target=handle_client, args=[c, privkey, lock, clients, conn])
                    t.start()
                except:
                    print("failed to send")
            else:
                print("beans")



def sendtoall(devices: dict[str: elecdevice],lock: threading.Lock, conn: sqlite3.Connection, curr: sqlite3.Cursor, clients: list):
    curr.execute("select * from plugs")
    build = curr.fetchall()
    print(build)
    for i in build:
        print(i)
        print(type(i[5]))
        x = i[5].replace("\'", "\"")
        print(x)
        d = elecdevice(i[0], i[1], i[2], i[4], i[3], json.loads(x))
        print(d.readings)
        devices = devices | {i[4]: d}
    ids = []
    while True:
        queries.discoverdevices(ids, curr, conn, devices)
        lock.acquire()
        print(ids)
        conn.commit()
        print(devices)
        send_to_client = []
        if ids is []:
            string = "no updates".encode()
        else:
            for i in ids:
                print(devices[i["name"]].ip)
                devices[i["name"]].ip = str(i["ip_address"])
                currently = datetime.datetime.now()
                print(i["electric_current"])
                devices[i["name"]].new_reading(currently.strftime("%d/%m/%Y %H:%M:%S"), str(i["electric_current"]), curr)
                send_to_client.append((i["name"],devices[i["name"]].readings))
            string = []
            print(devices)
            for i in devices:
                string.append((devices[i].name, devices[i].readings))
        print(clients)
        for c in clients:
            print(string)
            c.userclient.send(pickle.dumps(string))
            print("sent to" + str(c))
        lock.release()
        for i in range(15):
            print(15-i)
            time.sleep(1)

def hash(string: str):
    sha256 = hashlib.sha256()
    sha256.update(string.encode())
    string_hash = sha256.hexdigest()
    return string_hash

def main():
    HOST = "10.0.0.17"  # Standard loopback interface address (localhost)
    PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
    clients = []
    pubkey, privkey = rsa.newkeys(256)
    print(pubkey, privkey)
    devices = {}
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    lock = threading.Lock()
    conn = sqlite3.connect("/Users/amittelner/PycharmProjects/serverthing/database.db", check_same_thread=False)
    curr = conn.cursor()
    t1 = threading.Thread(target=get, args=[lock,pubkey,privkey,server,conn,clients])
    t2 = threading.Thread(target=sendtoall, args=[devices,lock, conn, curr, clients])
    t1.start()
    t2.start()




if __name__ == "__main__":
    try:
        main()
    except():
        print("buh bye")