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
    config['SETTINGS'] = {'key': 'F4', 'auto_disable': '4000'}  # Default keybind is F4 and auto-disable time is 4000 ms
    with open(config_file, 'w') as configfile:
        config.write(configfile)
else:
    config.read(config_file)

# Retrieve the keybind and auto-disable time from the config file
keybind = config['SETTINGS']['key']
auto_disable_time = int(config['SETTINGS']['auto_disable'])

# Create the main window
root = tk.Tk()
root.title("Lag Switch")
root.geometry("300x200")
root.configure(bg="#821131")  # Set background color
root.attributes('-alpha', 0.9)  # Set window transparency

# Lag switch status
lag_switch_on = False
timer = None

def release_internet():
    subprocess.run("ipconfig /release", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)

def renew_internet():
    subprocess.run("ipconfig /renew", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)

def auto_off_lag_switch():
    global lag_switch_on, timer
    if lag_switch_on and auto_disable_time > 0:
        timer = threading.Timer(auto_disable_time / 1000, disable_lag_switch)  # Convert ms to seconds
        timer.start()

def disable_lag_switch():
    global lag_switch_on, timer
    renew_internet()
    status_label.config(text="Lag Switch is OFF", fg="#FABC3F")
    lag_switch_on = False

def toggle_lag_switch():
    global lag_switch_on, timer
    if lag_switch_on:
        disable_lag_switch()
        if timer:
            timer.cancel()  # Cancel the auto-off timer
    else:
        release_internet()
        status_label.config(text="Lag Switch is ON", fg="#FABC3F")
        lag_switch_on = True
        auto_off_lag_switch()  # Start the auto-off timer

# Function to handle key press event for lag switch
def on_key_event(event):
    if event.name == keybind.lower():  # Check if the pressed key is the keybind
        toggle_lag_switch()

# Start listening for keyboard events without blocking
keyboard.hook(on_key_event)

# Status label to display the current state
status_label = tk.Label(root, text="Lag Switch is OFF", font=("Helvetica", 24), fg="#FABC3F", bg="#821131")
status_label.place(relx=0.5, rely=0.5, anchor='center')  # Center and position in the middle

# Function to change the keybind
def change_keybind():
    new_key = simpledialog.askstring("Change Keybind", "Enter new keybind:")
    if new_key:
        global keybind
        keybind = new_key
        config['SETTINGS']['key'] = new_key
        with open(config_file, 'w') as configfile:
            config.write(configfile)
        keyboard.remove_hotkey(keybind)  # Remove previous hotkey
        keyboard.add_hotkey(keybind, toggle_lag_switch)  # Rebind the new key
        messagebox.showinfo("Keybind Changed", f"Keybind changed to: {new_key}")

# Function to change the auto-disable time
def change_auto_disable():
    new_time = simpledialog.askinteger("Change Auto Disable Time", "Enter auto-disable time in ms (0 for manual control):", minvalue=0, maxvalue=60000)
    if new_time is not None:
        global auto_disable_time
        auto_disable_time = new_time
        config['SETTINGS']['auto_disable'] = str(new_time)
        with open(config_file, 'w') as configfile:
            config.write(configfile)
        if new_time == 0 and lag_switch_on:
            disable_lag_switch()  # Disable the lag switch if set to 0
        messagebox.showinfo("Auto Disable Time Changed", f"Auto-disable time changed to: {new_time} ms")

# Create a settings menu
def open_settings_menu():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("250x150")
    settings_window.configure(bg="#821131")  # Set background color
    settings_window.attributes('-alpha', 0.9)  # Set window transparency

    # Change Keybind Button
    change_keybind_button = tk.Button(settings_window, text="Change Keybind", command=change_keybind, bg="#C7253E", fg="#FABC3F", font=("Helvetica", 12))
    change_keybind_button.pack(pady=10)

    # Change Auto Disable Time Button
    change_auto_disable_button = tk.Button(settings_window, text="Change Auto Disable Time", command=change_auto_disable, bg="#C7253E", fg="#FABC3F", font=("Helvetica", 12))
    change_auto_disable_button.pack(pady=10)

# Button with three dots to open the settings menu
settings_button = tk.Button(root, text="⋮", command=open_settings_menu, font=("Helvetica", 14), bg="#E85C0D", fg="#FABC3F", borderwidth=0)
settings_button.place(x=10, y=10)  # Positioned in the top left corner

# Start the main loop
root.mainloop()
