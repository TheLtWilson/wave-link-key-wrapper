# 🔉 Wave Link Audio Wrapper

This is a Python script that allows you to turn keys on your keyboard into volume controls for Elgato's Wave Link software, and displays a simple popup of the current volume level.

Elgato leaves a websocket open, currently on port 1824, that is intended to be used to communicate between their Wave Link and Stream Deck software. I utilize this websocket connection to send actions based upon whatever the current volume or mute status is.

## ⚙️ How to Use

### Prerequisites

* Must be using Windows 10/11. This script does not support macOS.

* You will need to have Elgato's Wave Link software installed for this to work. This script works as of the version: `1.10.1 (2293)`

* Install the required dependencies with the command: `pip install -r requirements.txt`

### Running the Script

This small project was made to fit my own needs. If you want to change the keybindings, you will need to open the script and modify it yourself to fit your own needs.

I have the F13, F14, and F15 keys binded to a knob on my keyboard, as such the controls look like the following:

| Knob Direction    | Key           | Action       |
| ----------------- | ------------- | ------------ |
| Clockwise         | F13           | Volume Up    |
| Counter-clockwise | F14           | Volume Down  |
| Knob Button       | F15           | Toggle Mute  |

Once the script has been adjusted to your likings, you can simply run the script by opening it in your file manager and it will run in the background.

> ℹ️ **Notice:** My script assumes you always want the script to be running, so if you want to close the script you will need to end the Python process or implement your own hotkey.

### ⚠️ Handling Errors

Because the script is intended to run in the background without a terminal open, a log file is created in the directory where the script is located. This can be used to determine errors in the script, or get a gist of what the script is doing.