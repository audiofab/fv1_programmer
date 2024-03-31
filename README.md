# FV-1 Programmer

An FV-1 assembler/disassembler and EEPROM programming tool for the [Audiofab](https://audiofab.com/) [Easy Spin](https://audiofab.com/products/easy-spin) effects pedal.

This utility was made possible by the amazing [Textual](https://textual.textualize.io/) project. Check it out!

This utility also leverages the excellent FV-1 assembler ([asfv1](https://github.com/ndf-zz/asfv1)) and disassembler ([disfv1](https://github.com/ndf-zz/disfv1)).

# Installation

This utility requires Python 3.8 or greater. Alternatively, you can download one of the pre-built binaries for Windows, MacOS or Ubuntu Linux from the [releases page](https://github.com/audiofab/fv1_programmer/releases).

## Running From Python

If you are familiar with Python, this software is written in pure Python and can be installed using `pip` or `pipx`. If you prefer to install and run the tool using Python (such that it can be easily updated to the latest release using Python's packaging tools), the easiest way to install this utility is with Python's built-in `pip`. But keep in mind it will also install a bunch of dependencies directly into your Python environment:

`pip install fv1-programmer`

If you care about a clean Python environment, a cleaner way to install this utility is to first install [pipx](https://pypa.github.io/pipx/), and then install it with:

`pipx install fv1-programmer`

Either way, you will now have a `fv1_programmer` command on your path, which you can run in a terminal ([Windows Terminal](https://aka.ms/terminal) highly recommended on Windows):

```
$ fv1_programmer
```

This will bring up a user interface that will allow you to configure all 8 program slots of the Easy Spin's FV-1 DSP and write the EEPROM.

![image](https://github.com/audiofab/fv1_programmer/assets/1384978/36d8e9b9-4fe6-4cc4-b7b3-194910aaff97)

NOTE: On Linux you likely still need to install `libusb` and add a udev rule separately. See [Ubuntu Linux](README.md#Ubuntu-linux).

## Using One Of The Pre-Built Binaries

### Windows

On Windows, simply download the pre-built executable from the releases page and run it directly. No other dependencies are required. You may be warned by Microsoft Defender SmartScreen that this an unrecognized app. Rest assured it is safe - you can simply click the "More info" link and then click "Run anyway". You shouldn't be warned again.

Note: We still recommend you install [Windows Terminal](https://aka.ms/terminal) and set it to be your default terminal.

### MacOS

Currently, the application is built as an executable for MacOS, but you need to make it executable. To do this, open a terminal window; then 'cd' to the directory where you downloaded the fv1-programmer and type:

`chmod a+x fv1-programmer-macos-latest`

Once this is done, you will be able to run the software from the command line by typing

`./fv1-programmer-macos-latest`

You'll likely see a warning about being unable to execute a downloaded app and it may refuse to run it. If you see this, you can enable app execution by going to Apple menu > System Settings, then click Privacy & Security in the sidebar and select "Allow Anyway" for `fv1-programmer-macos-latest`.

### Ubuntu Linux

This application requires `libusb` on Linux. To install it, in a terminal run:

`sudo apt-get install libusb-1.0 libudev-dev`

After that, you will also need to set up a udev rule to allow access to the USB device. Use a text editor to create and edit the file `/etc/udev/rules.d/99-mcp2221.rules` and add the following contents:

`SUBSYSTEM=="usb", ATTRS{idVendor}=="04d8", ATTR{idProduct}=="00dd", MODE="0666"`

Finally, make the downloaded file executable. To do this, open a terminal; then 'cd' to the directory where you downloaded the fv1-programmer and type:

`chmod a+x fv1-programmer-ubuntu-latest`

Once this is done, you will be able to run the software from the command line by typing

`./fv1-programmer-ubuntu-latest`




# Known Issues

## Drag and drop not working reliably

On Windows 10 Terminal we have seen some issues with drag and drop not always working reliably. If you find that dragging a file from Explorer onto the application is not working, try dropping the file on the upper part of the user-interface (or even on the Program tabs) instead.