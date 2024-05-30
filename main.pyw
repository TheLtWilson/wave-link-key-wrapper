from pynput import keyboard
import json
import websocket
import time
import os
import threading
import logging
import tkinter as tk

# Parameters
step = 2
popup_duration = 2000
websocket_url = "ws://127.0.0.1:1824"

# Variables
operation_id = 1
current_volume = None
is_muted = None

# Change working directory to script location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Initialize logging
logging.basicConfig(
    filename="latest.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w"
)

# Initialize Tkinter
root = tk.Tk()
root.withdraw()

# WebSocket connection handler
def on_message(ws, message):
    global current_volume, is_muted
    response = json.loads(message)
    # Initial Volume Response
    if "result" in response:
        local_mixer = response["result"]["localMixer"]
        is_muted = local_mixer[0]
        current_volume = local_mixer[1]
        if current_volume is not None:
            logging.debug(f"Connection received current volume: {current_volume}")
    # Mute Status
    elif "method" in response and response["method"] == "outputMuteChanged":
        is_muted = response["params"]["value"]
        logging.debug(f"Mute changed to: {is_muted}")
        if is_muted:
            root.after(0, show_popup_message, f"󰖁 Muted ({current_volume})", "Output Volume")
        else:
            root.after(0, show_popup_message, f"󰕾 Unmuted ({current_volume})", "Output Volume")
    # Input Volumes
    elif "method" in response and response["method"] == "inputVolumeChanged":
        # System Input Volume
        if response["params"]["identifier"] == "PCM_OUT_01_V_00_SD2" and response["params"]["mixerID"] == "com.elgato.mix.local":
            logging.debug(f"System volume changed to: {response['params']['value']}")
            root.after(0, show_popup_message, f"󰕾 {response['params']['value']}", "System Volume")
        # Music Input Volume
        elif response["params"]["identifier"] == "PCM_OUT_01_V_02_SD3" and response["params"]["mixerID"] == "com.elgato.mix.local":
            logging.debug(f"Music volume changed to: {response['params']['value']}")
            root.after(0, show_popup_message, f"󰕾 {response['params']['value']}", "Music Volume")
        # Browser Input Volume
        elif response["params"]["identifier"] == "PCM_OUT_01_V_04_SD4" and response["params"]["mixerID"] == "com.elgato.mix.local":
            logging.debug(f"Browser volume changed to: {response['params']['value']}")
            root.after(0, show_popup_message, f"󰕾 {response['params']['value']}", "Browser Volume")
        # Voice Chat Input Volume
        elif response["params"]["identifier"] == "PCM_OUT_01_V_06_SD5" and response["params"]["mixerID"] == "com.elgato.mix.local":
            logging.debug(f"Voice Chat volume changed to: {response['params']['value']}")
            root.after(0, show_popup_message, f"󰕾 {response['params']['value']}", "Voice Chat Volume")
        # SFX Input Volume
        elif response["params"]["identifier"] == "PCM_OUT_01_V_08_SD6" and response["params"]["mixerID"] == "com.elgato.mix.local":
            logging.debug(f"SFX volume changed to: {response['params']['value']}")
            root.after(0, show_popup_message, f"󰕾 {response['params']['value']}", "SFX Volume")
        # Game Input Volume
        elif response["params"]["identifier"] == "PCM_OUT_01_V_10_SD7" and response["params"]["mixerID"] == "com.elgato.mix.local":
            logging.debug(f"Game volume changed to: {response['params']['value']}")
            root.after(0, show_popup_message, f"󰕾 {response['params']['value']}", "Game Volume")
        # Aux 1 Input Volume
        elif response["params"]["identifier"] == "PCM_OUT_01_V_12_SD8" and response["params"]["mixerID"] == "com.elgato.mix.local":
            logging.debug(f"Aux 1 volume changed to: {response['params']['value']}")
            root.after(0, show_popup_message, f"󰕾 {response['params']['value']}", "Aux 1 Volume")
        # Aux 2 Input Volume
        elif response["params"]["identifier"] == "PCM_OUT_01_V_14_SD9" and response["params"]["mixerID"] == "com.elgato.mix.local":
            logging.debug(f"Aux 2 volume changed to: {response['params']['value']}")
            root.after(0, show_popup_message, f"󰕾 {response['params']['value']}", "Aux 2 Volume")
    # Output Volumes
    elif "method" in response and response["method"] == "outputVolumeChanged":
        current_volume = response["params"]["value"]
        logging.debug(f"Volume changed to: {current_volume}")
        root.after(0, show_popup_message, f"󰕾 {current_volume}", "Output Volume")

# WebSocket error handler
def on_error(ws, error):
    logging.error(f"WebSocket error: {error}")

# WebSocket close handler
def on_close(ws, close_status_code, close_msg):
    logging.info(f"WebSocket connection was closed: {close_status_code} - {close_msg}")
    reconnect()

# WebSocket open handler
def on_open(ws):
    logging.info("WebSocket connection opened")
    volume_message = {
        "jsonrpc": "2.0",
        "method": "getOutputConfig",
        "id": operation_id
    }
    ws.send(json.dumps(volume_message))

# Function to increase volume
def increase_volume():
    if ws.sock.connected:
        logging.debug("Increase volume was called")
        global operation_id, current_volume
        if current_volume is not None:
            new_volume = current_volume + step
            volume_message = {
                "jsonrpc": "2.0",
                "method": "setOutputConfig",
                "id": operation_id,
                "params": {
                    "property": "Output Level",
                    "mixerID": "com.elgato.mix.local",
                    "value": new_volume,
                    "forceLink": False
                }
            }
            ws.send(json.dumps(volume_message))
            operation_id += 1
    else:
        logging.error("Increase volume was called, but the socket is closed")

# Function to decrease volume
def decrease_volume():
    if ws.sock.connected:
        logging.debug("Decrease volume was called") 
        global operation_id, current_volume
        if current_volume is not None:
            new_volume = current_volume - step
            volume_message = {
                "jsonrpc": "2.0",
                "method": "setOutputConfig",
                "id": operation_id,
                "params": {
                    "property": "Output Level",
                    "mixerID": "com.elgato.mix.local",
                    "value": new_volume,
                    "forceLink": False
                }
            }
            ws.send(json.dumps(volume_message))
            operation_id += 1
    else:
        logging.error("Decrease volume was called, but the socket is closed")

# Function to toggle mute
def toggle_mute():
    if ws.sock.connected:
        logging.debug("Toggle mute was called")
        global operation_id, is_muted
        mute_message = {
            "jsonrpc": "2.0",
            "method": "setOutputConfig",
            "id": operation_id,
            "params": {
                "property": "Output Mute",
                "mixerID": "com.elgato.mix.local",
                "value": not is_muted,
                "forceLink": False
            }
        }
        ws.send(json.dumps(mute_message))
        operation_id += 1
    else:
        logging.error("Toggle mute was called, but the socket is closed")

# Function to show volume popup
def show_popup_message(message, label):
    popup = tk.Toplevel(root)
    popup.overrideredirect(True)
    popup.geometry("220x80+50+50")  # width x height, pos x + pos y
    popup.attributes("-topmost", True)  # Ensure the popup appears on top
    
    # Dark mode styles
    background_color = "#333333"
    foreground_color = "#FFFFFF"
    border_color = "#555555"
    
    popup.config(bg=border_color)
    inner_frame = tk.Frame(popup, bg=background_color, bd=1, relief="solid")
    inner_frame.pack(expand=True, fill="both", padx=2, pady=2)
    
    type_label = tk.Label(inner_frame, text=str(label), font=("SpaceMono Nerd Font", 12), bg=background_color, fg=foreground_color)
    vol_label = tk.Label(inner_frame, text=str(message), font=("SpaceMono Nerd Font", 16, "bold"), bg=background_color, fg=foreground_color)

    type_label.pack(expand=True, fill="both")
    vol_label.pack(expand=True, fill="both")

    popup.after(popup_duration, popup.destroy)

# WebSocket setup
ws = websocket.WebSocketApp(
    websocket_url, 
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
    on_open=on_open
)

# Function to reconnect WebSocket
def reconnect():
    while True:
        try:
            logging.info("Attempting to reconnect to WebSocket")
            ws.run_forever()
            logging.info("Successfully reconnected to WebSocket")
            break
        except Exception as e:
            logging.error(f"Failed to reconnect to WebSocket: {e}")
            time.sleep(5)  # Wait before attempting to reconnect again

# Start WebSocket on separate thread
def run_ws():
    ws.run_forever()

ws.thread = threading.Thread(target=run_ws)
ws.thread.daemon = True
ws.thread.start()

# Handle keyboard presses through pynput
def on_press(key):
    try:
        if key == keyboard.Key.f13:
            increase_volume()
        elif key == keyboard.Key.f14:
            decrease_volume()
        elif key == keyboard.Key.f15:
            toggle_mute()
    except Exception as e:
        logging.error(f"Error handling key press: {e}")
    
# Start listening for keyboard events
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Start WebSocket listener
if __name__ == "__main__":
    logging.info("Script started")
    tk.mainloop()