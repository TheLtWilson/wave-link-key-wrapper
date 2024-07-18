from pynput import keyboard
from configparser import ConfigParser
from popup import showPopup, popupRoot
import json
import websocket
import time
import os
import threading
import logging

# Change working directory to script location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Classes
class Mixer:
    # These should not change.
    Local = "com.elgato.mix.local"
    Stream = "com.elgato.mix.stream"

class Input:
    # If you have more inputs, like an additional microphone, you should add and label them here
    System = "PCM_OUT_01_V_00_SD2"
    Music = "PCM_OUT_01_V_02_SD3"
    Browser = "PCM_OUT_01_V_04_SD4"
    VoiceChat = "PCM_OUT_01_V_06_SD5"
    SFX = "PCM_OUT_01_V_08_SD6"
    Game = "PCM_OUT_01_V_10_SD7"
    Aux1 = "PCM_OUT_01_V_12_SD8"
    Aux2 = "PCM_OUT_01_V_14_SD9"

class Outputs:
    # You can find your identifiers by running the script and checking the logs for "available outputs" or "selected output"
    Speakers = "HDAUDIO#FUNC_01&VEN_10EC&DEV_1168&SUBSYS_104387C5&REV_1001#5&32F1D1AA&0&0001#{6994AD04-93EF-11D0-A3CC-00A0C9223196}\\ELINEOUTWAVE"
    Headphones = "PCM_OUT_01_C_00_SD1"

# Variables
current_volume = None
is_muted = None
config = ConfigParser()

# Read config file
config.read("config.ini")

# Set variables from config
step = int(config.get("main", "step"))
websocket_url = str(config.get("main", "websocket_url"))

# Initialize logging
logging.basicConfig(
    filename="latest.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w"
)

# WebSocket connection handler
def on_message(ws, message):
    global current_volume, is_muted
    response = json.loads(message)
    # Operations without method key
    if "result" in response:
        # For initial volume
        if "localMixer" in response["result"]:
            local_mixer = response["result"]["localMixer"]
            is_muted = local_mixer[0]
            current_volume = local_mixer[1]
            if current_volume is not None:
                logging.debug(f"Connection received, current volume: {current_volume}")
        elif "outputs" in response["result"]:
            available_outputs = response["result"]["outputs"]
            selected_output = response["result"]["selectedOutput"]
            logging.debug(f"Available outputs: {json.dumps(available_outputs)}")
            logging.debug(f"Selected output: {json.dumps(selected_output)}")
    # Mute Status
    elif "method" in response and response["method"] == "outputMuteChanged":
        if response["params"]["mixerID"] == Mixer.Local:
            is_muted = response["params"]["value"]
            logging.debug(f"Mute changed to: {is_muted}")
            if is_muted:
                showPopup(f"󰖁 Muted ({current_volume})", "Output Volume")
            else:
                showPopup(f"󰕾 Unmuted ({current_volume})", "Output Volume")
        else:
            logging.debug(f"Mute changed on mixer: {response['params']['mixerID']} - {response['params']['value']}")
    # Input Mute Status
    elif "method" in response and response["method"] == "inputMuteChanged":
        logging.debug(f"Input mute changed on mixer: {response['params']['mixerID']}, identifier: {response['params']['identifier']} - {response['params']['value']}")
    # Input Volumes
    elif "method" in response and response["method"] == "inputVolumeChanged":
        # We only want to show the popup for one mixer, in this case the local mixer.
        # This is so we don't get multiple popups for the same volume change - notibly when faders are linked.
        if response["params"]["mixerID"] == Mixer.Local:
            match response["params"]["identifier"]:
                case Input.System:
                    logging.debug(f"System volume changed to: {response['params']['value']}")
                    showPopup(f"󰕾 {response['params']['value']}", "System Volume")
                case Input.Music:
                    logging.debug(f"Music volume changed to: {response['params']['value']}")
                    showPopup(f"󰕾 {response['params']['value']}", "Music Volume")
                case Input.Browser:
                    logging.debug(f"Browser volume changed to: {response['params']['value']}")
                    showPopup(f"󰕾 {response['params']['value']}", "Browser Volume")
                case Input.VoiceChat:
                    logging.debug(f"Voice Chat volume changed to: {response['params']['value']}")
                    showPopup(f"󰕾 {response['params']['value']}", "Voice Chat Volume")
                case Input.SFX:
                    logging.debug(f"SFX volume changed to: {response['params']['value']}")
                    showPopup(f"󰕾 {response['params']['value']}", "SFX Volume")
                case Input.Game:
                    logging.debug(f"Game volume changed to: {response['params']['value']}")
                    showPopup(f"󰕾 {response['params']['value']}", "Game Volume")
                case Input.Aux1:
                    logging.debug(f"Aux 1 volume changed to: {response['params']['value']}")
                    showPopup(f"󰕾 {response['params']['value']}", "Aux 1 Volume")
                case Input.Aux2:
                    logging.debug(f"Aux 2 volume changed to: {response['params']['value']}")
                    showPopup(f"󰕾 {response['params']['value']}", "Aux 2 Volume")
    # Output Volumes
    elif "method" in response and response["method"] == "outputVolumeChanged":
        if response["params"]["mixerID"] == Mixer.Local:
            current_volume = response["params"]["value"]
            logging.debug(f"Volume changed to: {current_volume}")
            showPopup(f"󰕾 {current_volume}", "Output Volume")
        else:
            logging.debug(f"Volume changed on mixer: {response['params']['mixerID']} - {response['params']['value']}")
    # Output Changes
    elif "method" in response and response["method"] == "selectedOutputChanged":
        logging.debug(f"Output changed to identifier: {response['params']['value']}")
        # For my specific setup these are the identifiers for my speakers and headphones
        # You can find your identifiers by running the script and checking the logs for "available outputs" or "selected output"
        if response["params"]["value"] == Outputs.Speakers:
            showPopup("󰓃 Speakers", "Output Changed")
        elif response["params"]["value"] == Outputs.Headphones:
            showPopup(" Headphones", "Output Changed")

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
    get_output_config()
    get_output_devices()

# Function to get output configuration
def get_output_config():
    volume_message = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "getOutputConfig"
    }
    ws.send(json.dumps(volume_message))

# Function to get available output devices
def get_output_devices():
    message = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "getOutputs",
    }
    ws.send(json.dumps(message))

# Function to change output device.
# This is not used in my use case, but can be used to set the current output device to a specific device.
# You can get your available output devices by running the script and checking the logs for "available outputs" or "selected output"
def change_output_device(identifier: str, name: str):
    # Only run if the socket is connected
    if ws.sock.connected:
        try:
            logging.debug(f"Change output device was called with identifier: {identifier} and name: {name}")
            message = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "setSelectedOutput",
                "params": {
                    "identifier": identifier,
                    "name": name
                }
            }
            ws.send(json.dumps(message))
        except Exception as e:
            logging.error(f"Error changing output device: {e}")
    else:
        logging.error("Change output device was called, but the socket is closed")

# Function to increase output volume by configured step
def increase_output_volume(mixer: Mixer):
    # Only run if the socket is connected
    if ws.sock.connected:
        try:
            logging.debug(f"Increase output volume was called on mixer: {mixer}")
            if current_volume is not None:
                # Increase current volume by step
                new_volume = current_volume + step
                # Set the volume to the new value on provided mixer
                set_output_volume(mixer, new_volume)
        except Exception as e:
            logging.error(f"Error increasing output volume: {e}")
    else:
        logging.error("Increase volume was called, but the socket is closed.")

# Function to decrease output volume by configured step
def decrease_output_volume(mixer: Mixer):
    # Only run if the socket is connected
    if ws.sock.connected:
        try:
            logging.debug(f"Decrease output volume was called on mixer: {mixer}") 
            if current_volume is not None:
                # Decrease current volume by step
                new_volume = current_volume - step
                # Set the volume to the new value on provided mixer
                set_output_volume(mixer, new_volume)
        except Exception as e:
            logging.error(f"Error decreasing output volume: {e}")
    else:
        logging.error("Decrease output volume was called, but the socket is closed.")

# Function to set output volume to a specific value
def set_output_volume(mixer: Mixer, volume: int):
    # Only run if the socket
    if ws.sock.connected:
        try:
            logging.debug(f"Set output volume was called on mixer: {mixer}")
            volume_message = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "setOutputConfig",
                "params": {
                    "property": "Output Level",
                    "mixerID": mixer,
                    "value": volume,
                    "forceLink": False
                }
            }
            ws.send(json.dumps(volume_message))
        except Exception as e:
            logging.error(f"Error setting output volume: {e}")
    else:
        logging.error("Set output volume was called, but the socket is closed")

# Function to set toggle the output mute state
def toggle_output_mute(mixer: Mixer):
    # Only run if the socket is connected
    if ws.sock.connected:
        try:
            # New mute state is the opposite of the current mute state
            new_mute_state = not is_muted
            # Set the new mute state on the provided mixer
            set_mute_output(mixer, new_mute_state)
        except Exception as e:
            logging.error(f"Error toggling output mute: {e}")
    else:
        logging.error("Toggle mute was called, but the socket is closed")

# Function to mute output
def set_mute_output(mixer: Mixer, value: bool):
    # Only run if the socket is connected
    if ws.sock.connected:
        try:
            logging.debug(f"Mute was called on mixer: {mixer}")
            mute_message = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "setOutputConfig",
                "params": {
                    "property": "Output Mute",
                    "mixerID": mixer,
                    "value": value,
                    "forceLink": False
                }
            }
            ws.send(json.dumps(mute_message))
        except Exception as e:
            logging.error(f"Error muting output: {e}")
    else:
        logging.error("Mute was called, but the socket is closed")

# Function to set input volume to a specific value
# This is not used in my use case, but can be used to set the volume of specific inputs.
# You can get the current volume of inputs by listening to the inputVolumeChanged method in the on_message function.
def set_input_volume(mixer: Mixer, identifier: Input, volume: int):
    # Only run if the socket is connected
    if ws.sock.connected:
        try:
            logging.debug(f"Set input volume was called on mixer: {mixer} and identifier: {identifier}")
            volume_message = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "setInputConfig",
                "params": {
                    "property": "Volume",
                    "identifier": identifier,
                    "mixerID": mixer,
                    "forceLink": False,
                    "value": volume
                }
            }
            ws.send(json.dumps(volume_message))
        except Exception as e:
            logging.error(f"Error setting input volume: {e}")
    else:
        logging.error("Set input volume was called, but the socket is closed")

# Same as function above, this also is not used in my use case, but can be used to mute specific inputs.
# You can get the mute state of inputs by listening to the inputMuteChanged method in the on_message function.
def set_input_mute(mixer: Mixer, identifier: Input, value: bool):
    # Only run if the socket is connected and when a mixer is provided
    if ws.sock.connected:
        try:
            logging.debug(f"Set input mute was called on mixer: {mixer} and identifier: {identifier}")
            mute_message = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "setInputConfig",
                "params": {
                    "property": "Mute",
                    "identifier": identifier,
                    "mixerID": mixer,
                    "forceLink": False,
                    "value": value
                }
            }
            ws.send(json.dumps(mute_message))
        except Exception as e:
            logging.error(f"Error setting input mute: {e}")
    else:
        logging.error("Set input mute was called, but the socket is closed")

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
            increase_output_volume(Mixer.Local)
        elif key == keyboard.Key.f14:
            decrease_output_volume(Mixer.Local)
        elif key == keyboard.Key.f15:
            toggle_output_mute(Mixer.Local)
    except Exception as e:
        logging.error(f"Error handling key press: {e}")
    
# Start listening for keyboard events
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Start WebSocket listener
if __name__ == "__main__":
    logging.info("Script started")
    # Start the Tkinter main loop for the volume popups
    popupRoot.mainloop()