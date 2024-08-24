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
    config['SETTINGS'] = {'key': 'F4', 'auto_disable': '4000', 'overlay': 'True'}  # Default keybind is F4 and auto-disable time is 4000 ms
    with open(config_file, 'w') as configfile:
        config.write(configfile)
else:
    config.read(config_file)

# Retrieve the keybind and auto-disable time from the config file
keybind = config['SETTINGS']['key']
auto_disable_time = int(config['SETTINGS']['auto_disable'])
overlay_enabled = config['SETTINGS'].getboolean('overlay')

# Create the main window
root = tk.Tk()
root.title("Lag Switch")
root.geometry("300x200")
root.configure(bg="#821131")  # Set background color
root.attributes('-alpha', 0.9)  # Set window transparency

# Lag switch status
lag_switch_on = False
timer = None

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
    status_label.config(text="Lag Switch is OFF")
    lag_switch_on = False
    update_overlay()

def toggle_lag_switch():
    global lag_switch_on, timer
    if lag_switch_on:
        disable_lag_switch()
        if timer:
            timer.cancel()  # Cancel the auto-off timer
    else:
        release_internet()
        status_label.config(text="Lag Switch is ON")
        lag_switch_on = True
        auto_off_lag_switch()  # Start the auto-off timer
    update_overlay()

# Function to handle key press event for lag switch
def on_key_event(event):
    if event.name == keybind.lower():  # Check if the pressed key is the keybind
        toggle_lag_switch()

# Start listening for keyboard events without blocking
keyboard.on_press(on_key_event)

# Status label to display the current state in the main window
status_label = tk.Label(root, text="Lag Switch is OFF", font=("Helvetica", 12), fg="#FABC3F", bg="#821131")
status_label.place(relx=0.5, rely=0.5, anchor='center')  # Center and position in the middle

def update_overlay():
    if overlay_enabled:
        if lag_switch_on:
            overlay_label.config(text="Lag Switch is ON")
        else:
            overlay_label.config(text="Lag Switch is OFF")
        overlay_window.deiconify()  # Show overlay window
    else:
        overlay_window.withdraw()  # Hide overlay window

# Function to change the keybind
def change_keybind():
    new_key = simpledialog.askstring("Change Keybind", "Enter new keybind:")
    if new_key:
        global keybind
        keybind = new_key
        config['SETTINGS']['key'] = new_key
        with open(config_file, 'w') as configfile:
            config.write(configfile)
        keyboard.unhook_all()  # Remove all keyboard hooks
        keyboard.on_press(on_key_event)  # Rebind the new key
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
            disable_lag_switch()  # Disable the lag switch if set to manual control
            messagebox.showinfo("Auto Disable Time Changed", f"Auto disable time changed to: {new_time} ms")

# Function to open the settings menu
def open_settings_menu():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("300x200")
    settings_window.configure(bg="#821131")

    # Change Keybind Button
    change_keybind_button = tk.Button(settings_window, text="Change Keybind", command=change_keybind, bg="#C7253E", fg="#FABC3F", font=("Helvetica", 12))
    change_keybind_button.pack(pady=10)

    # Change Auto Disable Time Button
    change_auto_disable_button = tk.Button(settings_window, text="Change Auto Disable Time", command=change_auto_disable, bg="#C7253E", fg="#FABC3F", font=("Helvetica", 12))
    change_auto_disable_button.pack(pady=10)

    # Overlay Toggle Button
    overlay_toggle_button = tk.Button(settings_window, text="Toggle Overlay", command=toggle_overlay, bg="#C7253E", fg="#FABC3F", font=("Helvetica", 12))
    overlay_toggle_button.pack(pady=10)

def toggle_overlay():
    global overlay_enabled
    overlay_enabled = not overlay_enabled
    config['SETTINGS']['overlay'] = str(overlay_enabled)
    with open(config_file, 'w') as configfile:
        config.write(configfile)
    update_overlay()
    if overlay_enabled:
        messagebox.showinfo("Overlay Toggled", "Overlay is now ON")
    else:
        messagebox.showinfo("Overlay Toggled", "Overlay is now OFF")

# Button with three dots to open the settings menu
settings_button = tk.Button(root, text="⋮", command=open_settings_menu, font=("Helvetica", 14), bg="#E85C0D", fg="#FABC3F", borderwidth=0)
settings_button.place(x=10, y=10)  # Positioned in the top left corner

# Initially hide overlay if not enabled
if not overlay_enabled:
    overlay_window.withdraw()

# Start the main loop
root.mainloop()
