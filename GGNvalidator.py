import online_checker as o

import tkinter as tk
from tkinter import filedialog
import json
import sys
import traceback

import subprocess
import threading 

import os

import ctypes
from pathlib import Path

# os.chdir(sys._MEIPASS)


# CWD = os.path.abspath(os.path.dirname(sys.executable))

# --- classes ---

class Redirect():

    def __init__(self, widget, autoscroll=True):
        self.widget = widget
        self.autoscroll = autoscroll

    def write(self, text):
        self.widget.insert('end', text)
        if self.autoscroll:
            self.widget.see("end")  # autoscroll
        
    def flush(self):
       pass

# --- functions ---

#UI

window = tk.Tk()
window.geometry("800x600")
window.title("GGN VALIDATOR")

title = tk.Label(text = "\nTHIS APP VALIDATES GGNs DIRECTLY ON GLOBAL GAP WEBSITE AND UPDATES DATABASE\n")
posttitle = tk.Label(text = "Copy GGNs into box below and press START")

subtitle = tk.Label(text = "BE PATIENT")

ggn_list_entry = tk.Text(window,height=10)
count_output = tk.Text(window, height=2)
time_output = tk.Text(window, height=2)
output = tk.Text(window, height=15, width=100)
scrollbar = tk.Scrollbar(window)

button_start = tk.Button(
    text="START",
    width=10,
    height=2,
    bg="red"
)

output['yscrollcommand'] = scrollbar.set
ggn_list_entry['yscrollcommand'] = scrollbar.set
scrollbar['command'] = output.yview


old_stdout = sys.stdout    
sys.stdout = Redirect(output)

def run(event):

    threading.Thread(target=run_prog).start()


def run_prog():
    ggn_list_string = ggn_list_entry.get("1.0",tk.END)
    try:
        o.check_ggns(ggn_list_string, tk, count_output, time_output, output)
        output.insert(tk.END,"\n\nDone!")
    except Exception as e:
        output.insert(tk.END,"\n\nSomething went wrong!\n" + str(e) +"\n" + str(traceback.format_exc()) + "\n" + str(sys.exc_info()[2]))

button_start.bind("<Button-1>", run)
title.pack()
posttitle.pack()
ggn_list_entry.pack()
button_start.pack()

count_output.pack()
time_output.pack()
output.pack()

scrollbar.pack(side='right', fill='y')
# output.pack(fill='both', expand=True)
# Create an event handler
subtitle.pack()

window.mainloop()

sys.stdout = old_stdout
