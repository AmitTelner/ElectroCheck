import customtkinter as ctk
import threading


class plug:

    def __init__(self,readings,name,x,frame:ctk.CTkFrame,measurements_frame, measurements_entry, widgets, lock):
        f = frame
        self.showbutton = ctk.CTkButton(master=f,text=name, width=15, height=2)
        self.showbutton.config(command=lambda:self.changeplug)
        self.showbutton.grid(row = 0, column = x)
        self.readings = readings
        self.name = name

    def changeplug(self):
       current_plug = self
       print(current_plug)