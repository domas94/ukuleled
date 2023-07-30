# TKINTER
import tkinter as tk
from tkinter import ttk

# MIDI
from mido import MidiFile, MidiFile, merge_tracks

# STANDARD LIB
import os
from threading import Thread
import time

# BLUETOTOH
import socket
import bluetooth







A4 = 69
E4 = 64
G4 = 67
C4 = 60
RANGE = 10


def exception_info(ex):
    """ Prints exception details. 
    """
    
    print("Error message:",ex)
    print("Error type: ",type(ex).__name__)
    tb = ex.__traceback__
    while tb is not None:
        print(str({"filename": tb.tb_frame.f_code.co_filename,"name": tb.tb_frame.f_code.co_name,"lineno": tb.tb_lineno}))
        tb = tb.tb_next

class Note:
    def __init__(self, note):
        self.note = note
        self.status = False
class Wires:
    def __init__(self):

        self.wire_1 = [i for i in range(A4, A4 + RANGE)] # 69 A4
        self.wire_2 = [i for i in range(E4, E4 + RANGE)] # 64 E4
        self.wire_3 = [i for i in range(C4, C4 + RANGE)] # 60 C4
        self.wire_4 = [i for i in range(G4, G4 + RANGE)] # 67 G4
        self.wires = [self.wire_1, self.wire_2, self.wire_3, self.wire_4]
        self.wire_status_1 = False
        self.wire_status_2 = False
        self.wire_status_3 = False
        self.wire_status_4 = False
        self.wire_statuses = [self.wire_status_1, self.wire_status_2, self.wire_status_3, self.wire_status_4]

wires = Wires()
note_status = [Note(i) for i in range(C4, A4 + RANGE)] 

thread_stop = False

def list_files_in_folder(folder_path):
    try:
        # Get a list of all files and directories in the specified folder
        file_list = os.listdir(folder_path)

        # Filter out only the files (exclude directories)
        files_only = [f for f in file_list if os.path.isfile(os.path.join(folder_path, f))]

        return files_only

    except FileNotFoundError:
        print(f"The specified folder '{folder_path}' does not exist.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def check_note_on(note_status, midi_note):
    retval = False
    for i in note_status:
        if i.note == midi_note:
            if i.status == True:
                retval = True
                break
    return retval

def set_note_on(midi_note, wires):
    retval = None
    for row, wire in enumerate(wires.wires):
        for wire_note in wire:
            if wire_note == midi_note and wires.wire_statuses[row] == False:
                column = 9 - (midi_note - wire[0])
                if column == 9:
                    key = 51
                else:
                    key = 49
                retval = chr(key) + chr(row) + chr(column) + chr(0) + chr(0) + chr(0)
                wires.wire_statuses[row] = True
                return retval

def set_note_off(midi_note, wires):
    retval = None
    for row, wire in enumerate(wires.wires):
        if midi_note in wire and wires.wire_statuses[row] == True:
            column = 9 - (midi_note - wire[0])
            if column == 9:
                key = 52
            else:
                key = 48
            retval = chr(key) + chr(row) + chr(column) + chr(0) + chr(0) + chr(0)
            wires.wire_statuses[row] = False
            return retval

def set_status_note(note_status, status, midi_note):
     for i in note_status:
        if i.note == midi_note:
            i.status = status
            break

def play_midi(midi_path, output_text, slider_value):
    global thread_stop
    def tick2second(tick, ticks_per_beat, tempo):
        """Convert absolute time in ticks to seconds.

        Returns absolute time in seconds for a chosen MIDI file time
        resolution (ticks per beat, also called PPQN or pulses per quarter
        note) and tempo (microseconds per beat).
        """
        scale = tempo * 1e-6 / ticks_per_beat
        return tick * scale

    def print_track_info(mid):
        for i, track in enumerate(mid.tracks):
            print('Track {}: {}'.format(i, track.name))
            for msg in track:
                print(msg)
    

    mid = MidiFile(midi_path)
    mid_merge = merge_tracks(mid.tracks)
    print(f"MIDI TYPE: {mid.type}")
    print(f"MIDI LENGTH: {mid.length}")
    print(f"TRACK LENGTH: {len(mid.tracks)}")
    total_time = 0
    thread_stop = False
    try:
        for msg in mid_merge:
            if thread_stop:
                break
            if msg.type == "set_tempo":
                tempo = msg.tempo / (slider_value/100)
            if (msg.time > 0):
                delta = tick2second(msg.time, mid.ticks_per_beat, tempo)
                total_time += delta
                time.sleep(delta)
            else:
                delta = 0
            midi_note_status = msg.dict().get('type')
            if midi_note_status == "note_on" or midi_note_status == "note_off":
                midi_note = msg.bytes()[1]
                velocity = msg.bytes()[2]
                if midi_note_status == "note_on" and velocity > 0:
                    retval = check_note_on(note_status, midi_note)
                    if retval == False:
                        retval = set_note_on(midi_note, wires)
                        if retval != None :
                            set_status_note(note_status, True, midi_note)
                        if retval != None and can_connect:
                            client.send(retval.encode("utf-8"))
                       
                elif midi_note_status == "note_off" and velocity == 0:
                    retval = set_note_off(midi_note, wires)
                    
                    if retval != None:
                        set_status_note(note_status, False, midi_note)
                    if retval != None and can_connect:
                        client.send(retval.encode("utf-8"))

                output_text.delete(1.0, tk.END)  # Clear previous output
                output_text.insert(tk.END, str(midi_note_status)+"\n")
                output_text.insert(tk.END, f"NOTE: {midi_note}\n")
                output_text.insert(tk.END, f"VELOCITY:{velocity}\n")
                output_text.insert(tk.END, f"TIME: {total_time}\n")
            
    except KeyboardInterrupt:
        print("KEYBOARD INTERRUPT MIDI PLAYING")
    except Exception as ex:
        exception_info(ex)
    print("THREAD STOPPED!")

folder_path_here = './'
files_in_folder = list_files_in_folder(folder_path_here)
midi_list = []
if files_in_folder:
    for file in files_in_folder:
        if ".mid" in file:
            midi_list.append(file)
else:
    print("No files found in the folder.")

def change_text():
    midi_song = selected_var.get()

    output_text.delete(1.0, tk.END)  # Clear previous output
    output_text.insert(tk.END, f"Selected Option: {midi_song}\n")
    output_text.insert(tk.END, f"Scale mode: {scale_mode_state.get()}\n")
    output_text.insert(tk.END, f"Slider value: {slider.get()}\n")
    output_text.insert(tk.END, f"Entry value: {entry.get()}\n")

    if ".mid" in midi_song:
        thread = Thread(target = play_midi, daemon = True, args = (midi_song, output_text, slider.get()))
        thread.start()

def stop_thread():
    global thread_stop
    thread_stop = True

# Create the main window
root = tk.Tk()
root.title("ukuleLED")

# Create a label and start_button widgets
label = tk.Label(root, text="UkuleLED player")
start_button = tk.Button(root, text="START", command=change_text)

stop_button = tk.Button(root, text="STOP", command=stop_thread)

# Create a StringVar to store the selected option from the dropdown menu
selected_var = tk.StringVar(root)
selected_var.set("Select a song")

# Create a dropdown menu
dropdown_menu = ttk.Combobox(root, textvariable=selected_var, values=midi_list)

# Create IntVars to store the state of the checkboxes
scale_mode_state = tk.IntVar(root)

# Create the checkboxes
scale_mode_checkbox = tk.Checkbutton(root, text=f"Scale mode", variable = scale_mode_state)

# Create a slider
slider = tk.Scale(root, from_= 50, to = 200, orient=tk.HORIZONTAL)
slider.set(100)
# Create a text output area
output_text = tk.Text(root, height=10, width=30)

# Create an entry
entry = tk.Entry(root, width=30)  # Adjust the width as needed
correct_device = "EC:62:60:84:17:DE"
entry.insert(0, correct_device)
nearby_devices = bluetooth.discover_devices(duration = 1, lookup_names=True)
bluetooth_info = tk.Label(root, text = f"Found {len(nearby_devices)} devices.")
bluetooth_string = ""
can_connect = False
can_connect_string = "DISCONNECTED"
entry.get()
for addr, name in nearby_devices:
    bluetooth_string += f"{addr} - {name}\n"
    if addr == correct_device:
        can_connect = True
bluetooth_info_2 = tk.Label(root, text = bluetooth_string)
client = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
if can_connect:
    client.connect((correct_device, 1)) 
    can_connect_string = "CONNECTED"
bluetooth_info_3 = tk.Label(root, text = can_connect_string)

# Place the widgets on the window
label.pack(pady=10)
entry.pack(pady=10)
bluetooth_info.pack()
bluetooth_info_2.pack()
bluetooth_info_3.pack()
dropdown_menu.pack()
slider.pack()
scale_mode_checkbox.pack()
start_button.pack(pady=10)
stop_button.pack(pady=10)
# Pack the checkboxes using a loop
output_text.pack(pady=10)

# Start the GUI event loop
root.mainloop()

client.close()
