# 🔉 Wave Link Key Wrapper

This is a Python script that allows you to turn keys on your keyboard into volume controls for Elgato's Wave Link software, and displays a simple popup of the current volume level.

Elgato leaves a websocket open, currently on port `1824`, that is intended to be used to communicate between their Wave Link and Stream Deck software. I utilize this websocket connection to send actions based upon whatever the current volume or mute status is.

## ⚙️ How to Use

### Prerequisites

* Must be using Windows 10/11. This script does not support macOS.

> [!NOTE]
> If you just want to use the script to control Wave Link and you **remove** the popup functionality, it *should* be compatible with macOS. I don't have a machine to test this on, so take this with a grain of salt.

* You will need to have Elgato's Wave Link software installed for this to work. This script works as of the version: `1.11.1 (2824)`

* A "nerd font" is required to properly display icons. I use [SpaceMono](https://github.com/ryanoasis/nerd-fonts/releases/download/v3.2.1/SpaceMono.zip), but you can change the font to one of your chosing here: [nerdfonts.com](https://nerdfonts.com)

### Installation

* Clone the repo with the command: `git clone https://github.com/TheLtWilson/wave-link-audio-wrapper`

* In the cloned folder, install the required dependencies with the command: `pip install -r requirements.txt`


### Running the Script

This small project was made to fit my own needs. If you want to change the keybindings, you will need to open the script and modify it yourself to fit your own needs.

I have the F13, F14, and F15 keys binded to a knob on my keyboard, as such the controls look like the following:

| Knob Direction    | Key           | Action       |
| ----------------- | ------------- | ------------ |
| Clockwise         | F13           | Volume Up    |
| Counter-clockwise | F14           | Volume Down  |
| Knob Button       | F15           | Toggle Mute  |

Once the script has been adjusted to your likings, you can simply run the script by opening it in your file manager and it will run in the background.

You can run the script on startup by adding a shortcut to it in your `shell:startup` folder.

> ℹ️ **Notice:** My script assumes you always want the script to be running, so if you want to close the script you will need to end the Python process or implement your own hotkey.

## 📃 Available Functions

Here is a list of basic Wave Link functions that you can use to shape your own project to whatever fits for you.

|Function|Description|Example|
|-|-|-|
|get_output_config()|This function is ran when the script starts, and provides initial data for the volume and mute status of each mixer.|get_output_config()|
|get_output_devices()|This function is ran when the script starts, and displays all available output devices, and the currently selected output device in the log. You should add and label your output devices in the Output class.|get_output_devices()|
|change_output_device(`device: class Output`)|Changes the current output device to the one provided. You'll need to use the `get_output_devices()` function to setup your output class.'|change_output_device(Output.Speakers)|
|set_output_volume(`mixer: class Mixer`, `volume: int`)|Sets the output volume on the specified mixer to the provided volume.|set_output_volume(Mixer.Stream, 75)|
|set_output_mute(`mixer: class Mixer`, `value: bool`)|Sets the output mute status on the specified mixer to the provided value.|set_output_mute(Mixer.Local, True)|
|set_input_volume(`mixer: class Mixer`, `identifier: class Input`, `volume: int`)|Sets the volume of a specified input on the specified mixer to the provided volume.|set_input_volume(Mixer.Local, Input.Browser, 50)|
|set_input_mute(`mixer: class Mixer`, `identifier: class Input` `value: bool`)|Sets the specified input mute status to the specified mixer to the provided value.|set_input_mute(Mixer.Stream, Input.Game, False)|

Functions for my use case:

> [!WARNING]
> I don't actually keep track of the volume of the stream mixer. So passing a different mixer to these functions doesn't actually do anything. I'll fix it eventually.

|Function|Description|Example|
|-|-|-|
|increase_output_volume(`mixer: class Mixer`)|Gets the current output volume, and increases it by the step in the config file. It calls `set_output_volume()` to set the volume.|increase_output_volume(Mixer.Local)|
|decrease_output_volume(`mixer: class Mixer`)|Gets the current output volume, and decreases it by the step in the config file. It calls `set_output_volume()` to set the volume.|decrease_output_volume(Mixer.Local)|
|toggle_output_mute(`mixer: class Mixer`)|Gets the mute status of the output, and sets it to the opposite to toggle it. It calls `set_output_mute()` to set the volume.|toggle_output_mute(Mixer.Local)|

## ⚠️ Handling Errors

Because the script is intended to run in the background without a terminal open, a log file is created in the directory where the script is located. This can be used to determine errors in the script, or get a gist of what the script is doing. As a matter of fact, you'll need to check the logs when you first start the script so that you can modify the script to include your own output devices.