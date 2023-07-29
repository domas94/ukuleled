import tkinter as tk
from tkinter import ttk
import time
from mido import MidiFile, MidiFile, merge_tracks
import os
from threading import Thread

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

def play_midi(midi_path, output_text):
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
                tempo = msg.tempo
            if (msg.time > 0):
                delta = tick2second(msg.time, mid.ticks_per_beat, tempo)
                time.sleep(delta)
                total_time += delta
            else:
                delta = 0
            note_status = msg.dict().get('type')
            if note_status == "note_on" or note_status == "note_off":
                note = msg.bytes()[1]
                velocity = msg.bytes()[2]
                output_text.delete(1.0, tk.END)  # Clear previous output
                output_text.insert(tk.END, str(note_status)+"\n")
                output_text.insert(tk.END, f"NOTE: {note}\n")
                output_text.insert(tk.END, f"VELOCITY:{velocity}\n")
                output_text.insert(tk.END, f"TIME: {total_time}\n")
            
    except KeyboardInterrupt:
        print("KEYBOARD INTERRUPT MIDI PLAYING")
    except Exception as ex:
        print(ex)
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
        thread = Thread(target = play_midi, args = (midi_song, output_text))
        thread.start()

def stop_thread():
    global thread_stop
    thread_stop = True

# Create the main window
root = tk.Tk()
root.title("ukuleLED")

# Create a label and button widgets
label = tk.Label(root, text="UkuleLED player")
button = tk.Button(root, text="Play MIDI", command=change_text)

stop_button = tk.Button(root, text="STOP MIDI", command=stop_thread)

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

# Place the widgets on the window
label.pack(pady=10)
slider.pack()
entry.pack(pady=10)
button.pack(pady=10)
stop_button.pack(pady=10)
dropdown_menu.pack()
# Pack the checkboxes using a loop
scale_mode_checkbox.pack(anchor=tk.W)
output_text.pack(pady=10)

# Start the GUI event loop
root.mainloop()

