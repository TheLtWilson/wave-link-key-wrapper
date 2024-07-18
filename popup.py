import tkinter as tk
import logging
from configparser import ConfigParser
from win32 import win32gui
import win32con
import os

# Change working directory to script location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Initialize Tkinter
popupRoot = tk.Tk()
popupRoot.withdraw()

# Read config file
config = ConfigParser()
config.read("config.ini")

# Set variables from config
popup_duration = int(config.get("main", "popup_duration"))
exp_fullscreen_taskbar_fix = bool(config.get("experimental", "fullscreen_taskbar_fix"))

def showPopup(message: str, label: str):
    popupRoot.after(0, _createPopupMessage, message, label)

def _createPopupMessage(message: str, label: str):
    try:
        popup = tk.Toplevel(popupRoot) # Create a new window
        popup.overrideredirect(True) # Remove window decorations
        popup.geometry("220x80+50+50")  # width x height, pos x + pos y
        popup.attributes("-topmost", True)  # Ensure the popup appears on top
        
        # Dark mode styles
        background_color = "#333333"
        foreground_color = "#FFFFFF"
        border_color = "#555555"
        
        # The frame that holds the content
        popup.config(bg=border_color)
        inner_frame = tk.Frame(popup, bg=background_color, bd=1, relief="solid")
        inner_frame.pack(expand=True, fill="both", padx=2, pady=2)
        
        # The labels that show the message and label
        type_label = tk.Label(inner_frame, text=str(label), font=("SpaceMono Nerd Font", 12), bg=background_color, fg=foreground_color)
        vol_label = tk.Label(inner_frame, text=str(message), font=("SpaceMono Nerd Font", 16, "bold"), bg=background_color, fg=foreground_color)
        type_label.pack(expand=True, fill="both")
        vol_label.pack(expand=True, fill="both")

        # Hide the popup after a set duration
        popup.after(popup_duration, popup.destroy)
        
        # Hacky way to make sure it doesn't make the taskbar appear in (most) fullscreen apps
        if exp_fullscreen_taskbar_fix:        
            hwnd = popup.winfo_id()
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            style = style | win32con.WS_EX_TOOLWINDOW
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)
    except Exception as e:
        logging.error(f"Error showing popup message: {e}")