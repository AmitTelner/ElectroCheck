import socket
import select
import time
import customtkinter as ctk
import tkinter as tk
import threading
import pickle
import rsa
#from plug import *



class plug:

    def __init__(self,readings,name,x,frame:tk.Frame, measurements_frame: tk.Frame, measurements_button: tk.Button, measurements_Entry: tk.Entry, widgets, lock):
        f = frame
        self.showbutton = tk.Button(master=f,text=name, width=15, height=2,command=lambda:self.changeplug(measurements_button, measurements_frame, measurements_Entry, widgets, lock))
        self.showbutton.grid(row = 0, column = x)
        self.readings = readings
        self.name = name

    def changeplug(self, measurements_button, measurements_frame, measurements_entry, widgets, lock):
       measurements_button.config(command=lambda:changemeasurements(measurements_frame,self.readings,measurements_entry.get(),widgets,self,lock))
       print("naggers")

class fakeplug:
    def __init__(self):
        self.readings = {'1':'2'}
        self.name = "bobby"

    def changeplug(self):
        print("mustard")


def send(usertext,passwordtext, pubkey, client):
    client.send(rsa.encrypt(str(usertext + "," + passwordtext).encode("utf8"), pubkey))
    print("sent")


def get(client: socket.socket, plug_pos: int, plugs: dict, enter_username_text: ctk.CTkLabel,
        user_entry: ctk.CTkEntry, enter_password_text: ctk.CTkLabel,message_entry: ctk.CTkEntry,send_button: ctk.CTkButton,
        measurements_text:ctk.CTkLabel,measurements_entry: ctk.CTkEntry,measurements_frame: ctk.CTkFrame, measurements_button: ctk.CTkButton,
        currentplug: plug, widgets: list,plugframe: ctk.CTkFrame, lock):
    #t1 = threading.Thread(target=get, args=[client, plugpos, plugs, enter_username_text,user_entry,enter_password_text,message_entry,send_button, measurements_text,measurements_entry,measurements_frame,number_of_measurements,measurements_button,currentplug, widgets,plug_frame, lock])

    while True:
        try:
            data = client.recv(1024)
            print(data)
            if not data:
                break
            try:
                message = pickle.loads(data)
                print('pickle')
                print(message)
                if message is not None:
                    for i in message:
                        print(plugs)
                        print(plugs.keys())
                        print(i)
                        if i[0] in plugs.keys():
                            print("lemons")
                            plugs[i[0]].readings = i[1]
                        else:
                            p = plug(i[1],i[0], plug_pos, plugframe, measurements_frame, measurements_button, measurements_entry, widgets, lock)
                            print("new plug lol")
                            print(p.name)
                            plugs = plugs | {p.name: p}
                            print('willies')
                            plug_pos+=1
                            print(plugs)
                            print(p)
                            print(type(currentplug))
                            if type(currentplug) == "<class '__main__.fakeplug'>" or currentplug == None:
                                currentplug = p
                                changemeasurements(plugframe, currentplug.readings, measurements_entry.get(), widgets,
                                               currentplug, lock)

            except:
                print("not a pickle")
                print(data)
                if data.decode() == "welcome":
                    enter_username_text.destroy()
                    user_entry.destroy()
                    enter_password_text.destroy()
                    message_entry.destroy()
                    send_button.destroy()
                    measurements_text.pack()
                    measurements_entry.pack()
                    measurements_button.pack()
                    measurements_frame.pack()
                    for i in range(1):
                        date = ctk.CTkLabel(master= measurements_frame,text='No date yet', height=1, width=20)
                        current = ctk.CTkLabel(master= measurements_frame, text='No measurement', height=1, width = 20)
                        date.grid(row = i, column = 0)
                        current.grid(row = i, column = 1)
                        widgets.append((date, current))


        except:
            print("failure")


def changemeasurements(frame: tk.Frame, readings: dict, num, widgets: list, current_plug,lock: threading.Lock):
    lock.acquire()
    print(current_plug.name)
    #try:
    print(current_plug)
    if True:
        if current_plug is not None:
            print(widgets)
            for i in widgets:
                i[0].destroy()
                i[1].destroy()
            n = 0
            print('phew')
            if num.isnumeric():
                number_of_measurements = int(num)
                print('lemons')
                print(readings)
                print(len(readings))
                print(num)
                for i in readings:
                    if n < int(num):
                        print(i)
                        print(n)
                        date = tk.Label(master=frame, text=str(i))
                        power = tk.Label(master=frame, text=readings[i])
                        widgets.append((date, power))
                        date.grid(row=n, column=0)
                        power.grid(row=n, column=1)
                        n+=1
                    else:
                        print("wario")
                        break


    #except:
        #print("num must be an integer")
    lock.release()



def main():
    HOST = "10.0.0.17"  # The server's hostname or IP address
    PORT = 65432  # The port used by the server
    client = socket.socket()
    client.connect((HOST, PORT))
    pubkey = pickle.loads(client.recv(1024))
    print(pubkey)
    plugs = {}
    currentplug = fakeplug()
    root = ctk.CTk()
    ctk.set_appearance_mode("dark")
    root.title("ElectroCheck")
    plugpos = 0
    enter_username_text = ctk.CTkLabel(master = root, text="enter username")
    user_entry = ctk.CTkEntry(master = root, width = 150)
    enter_password_text = ctk.CTkLabel(master = root, text="enter password")
    message_entry = ctk.CTkEntry(master=root, width=150)
    plug_frame = ctk.CTkFrame(master=root)
    measurements_text = ctk.CTkLabel(master=root,text="Enter number of measurements")
    measurements_entry = ctk.CTkEntry(master=root,width=150)
    widgets = []
    lock = threading.Lock()
    measurements_frame = ctk.CTkFrame(master=root)
    measurements_button = ctk.CTkButton(master=root, width = 3, height = 2,text='push',command=lambda:changemeasurements(measurements_frame,currentplug.readings,measurements_entry.get(),widgets,currentplug,lock))
    send_button = ctk.CTkButton(master=root, width=5, height=3, text="send", command=lambda:send(user_entry.get(),message_entry.get(), pubkey, client))
    plug_frame.pack()
    enter_username_text.pack()
    user_entry.pack()
    enter_password_text.pack()
    message_entry.pack()
    send_button.pack()
    t1 = threading.Thread(target=get, args=[client, plugpos, plugs, enter_username_text,user_entry,enter_password_text,message_entry,send_button, measurements_text,measurements_entry,measurements_frame,measurements_button,currentplug, widgets,plug_frame, lock])
    t1.start()
    root.mainloop()


if __name__ == "__main__":
    main()

