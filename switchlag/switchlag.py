import tkinter as tk
from tkinter import messagebox, simpledialog
import keyboard
import subprocess
import configparser
import os
import threading

# Config file setup
config_file = 'config.ini'
config = configparser.ConfigParser()

# Load or create the config file
if not os.path.exists(config_file):
    config['KEYBINDS'] = {'f4': '4000'}  # Default keybind F4 with 4000 ms delay
    config['SETTINGS'] = {'overlay': 'True'}
    with open(config_file, 'w') as configfile:
        config.write(configfile)
else:
    config.read(config_file)

# Retrieve the overlay setting from the config file
overlay_enabled = config['SETTINGS'].getboolean('overlay')

# Create the main window
root = tk.Tk()
root.title("Lag Switch")
root.geometry("400x300")
root.configure(bg="#821131")  # Set background color
root.attributes('-alpha', 0.9)  # Set window transparency

# Lag switch status
lag_switch_on = {}
timers = {}

# Create the overlay window
overlay_window = tk.Toplevel(root)
overlay_window.attributes('-topmost', True, '-alpha', 0.7)
overlay_window.overrideredirect(True)
overlay_window.configure(bg='black')

# Position the overlay window in the bottom right corner of the screen
def position_overlay():
    screen_width = overlay_window.winfo_screenwidth()
    screen_height = overlay_window.winfo_screenheight()
    overlay_window.geometry(f"300x50+{screen_width - 310}+{screen_height - 60}")

position_overlay()  # Set the initial position

# Overlay label to display the current state
overlay_label = tk.Label(overlay_window, text="", font=("Helvetica", 20), fg="#FABC3F", bg="black")
overlay_label.pack(expand=True, fill='both')

# Functions to release and renew internet
def release_internet():
    subprocess.run("ipconfig /release", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)

def renew_internet():
    subprocess.run("ipconfig /renew", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)

# Disable the lag switch
def disable_lag_switch(key):
    if key in timers and timers[key]:
        timers[key].cancel()
    renew_internet()
    lag_switch_on[key] = False
    update_status()
    update_overlay()

# Toggle the lag switch
def toggle_lag_switch(key, delay):
    if delay == 0:  # Manual control
        if lag_switch_on.get(key, False):
            disable_lag_switch(key)
        else:
            release_internet()
            lag_switch_on[key] = True
            update_status()
    else:
        if lag_switch_on.get(key, False):
            disable_lag_switch(key)
        else:
            release_internet()
            lag_switch_on[key] = True
            update_status()
            if delay > 0:
                timers[key] = threading.Timer(delay / 1000, lambda: disable_lag_switch(key))
                timers[key].start()
    update_overlay()

# Function to handle key press event for lag switch
def on_key_event(event):
    key = event.name.lower()
    if key in config['KEYBINDS']:
        delay = int(config['KEYBINDS'][key])
        toggle_lag_switch(key, delay)

# Start listening for keyboard events without blocking
keyboard.on_press(on_key_event)

# Update the overlay
def update_overlay():
    if overlay_enabled:
        if any(lag_switch_on.values()):  # Check if any lag switch is ON
            overlay_label.config(text="Lag Switch is ON")
            overlay_window.deiconify()  # Show overlay window
        else:
            overlay_label.config(text="Lag Switch is OFF")
            overlay_window.deiconify()  # Show overlay window
    else:
        overlay_window.withdraw()  # Hide overlay window

# Update the status in the main window
def update_status():
    status_text = ""
    for key, delay in config['KEYBINDS'].items():
        status = "ON" if lag_switch_on.get(key, False) else "OFF"
        status_text += f"{key.upper()} - {delay} ms: {status}\n"
    status_label.config(text=status_text.strip())

# Function to add a new keybind
def add_keybind():
    new_key = simpledialog.askstring("Add Keybind", "Enter new key:")
    new_time = simpledialog.askinteger("Auto Disable Time", "Enter auto-disable time in ms (0 for manual control):", minvalue=0, maxvalue=60000)
    if new_key and new_time is not None:
        config['KEYBINDS'][new_key.lower()] = str(new_time)
        with open(config_file, 'w') as configfile:
            config.write(configfile)
        update_status()
        messagebox.showinfo("Keybind Added", f"Keybind {new_key.upper()} added with {new_time} ms delay.")

# Function to remove a keybind
def remove_keybind():
    key_to_remove = simpledialog.askstring("Remove Keybind", "Enter key to remove:")
    if key_to_remove and key_to_remove.lower() in config['KEYBINDS']:
        del config['KEYBINDS'][key_to_remove.lower()]
        with open(config_file, 'w') as configfile:
            config.write(configfile)
        lag_switch_on.pop(key_to_remove.lower(), None)
        update_status()
        update_overlay()
        messagebox.showinfo("Keybind Removed", f"Keybind {key_to_remove.upper()} removed.")

# Function to open the settings menu
def open_settings_menu():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("300x200")
    settings_window.configure(bg="#821131")

    # Add Keybind Button
    add_keybind_button = tk.Button(settings_window, text="Add Keybind", command=add_keybind, bg="#C7253E", fg="#FABC3F", font=("Helvetica", 12))
    add_keybind_button.pack(pady=10)

    # Remove Keybind Button
    remove_keybind_button = tk.Button(settings_window, text="Remove Keybind", command=remove_keybind, bg="#C7253E", fg="#FABC3F", font=("Helvetica", 12))
    remove_keybind_button.pack(pady=10)

    # Overlay Toggle Button
    overlay_toggle_button = tk.Button(settings_window, text="Toggle Overlay", command=toggle_overlay, bg="#C7253E", fg="#FABC3F", font=("Helvetica", 12))
    overlay_toggle_button.pack(pady=10)

# Toggle the overlay visibility
def toggle_overlay():
    global overlay_enabled
    overlay_enabled = not overlay_enabled
    config['SETTINGS']['overlay'] = str(overlay_enabled)
    with open(config_file, 'w') as configfile:
        config.write(configfile)
    update_overlay()
    messagebox.showinfo("Overlay Toggled", f"Overlay is now {'ON' if overlay_enabled else 'OFF'}")

# Status label to display the current state in the main window
status_label = tk.Label(root, text="", font=("Helvetica", 12), fg="#FABC3F", bg="#821131", justify="left")
status_label.place(relx=0.5, rely=0.5, anchor='center')

# Label for Keybinds/ms
keybinds_label = tk.Label(root, text="Keybinds/ms:", font=("Helvetica", 14), fg="#FABC3F", bg="#821131")
keybinds_label.place(relx=0.5, y=20, anchor='center')

# Button with three dots to open the settings menu
settings_button = tk.Button(root, text="⋮", command=open_settings_menu, font=("Helvetica", 20), bg="#E85C0D", fg="#FABC3F", borderwidth=0)
settings_button.place(x=10, y=10)  # Positioned in the top left corner

# Initially hide overlay if not enabled
if not overlay_enabled:
    overlay_window.withdraw()

# Update status and overlay initially
update_status()
update_overlay()

# Start the main loop
root.mainloop()
