# FV-1 Programmer

An EEPROM programming tool for the [Audiofab](https://audiofab.com/) [Easy Spin](https://audiofab.com/products/easy-spin) effects pedal.

# Installation

This utility requires Python 3.8 or greater and has been tested on Windows, but should also work on MacOS and Linux. 

The easiest way to install this utility is with Python's built-in pip but it will also install a bunch of dependencies directly into your Python environment:

`pip install fv1-programmer`

If you care about a clean Python environment, a cleaner way to install this utility is to first install [pipx](https://pypa.github.io/pipx/), and then install it with:

`pipx install fv1-programmer`

Either way, you will now have a `fv1_programmer` command on your path, which you can run in a terminal ([Windows Terminal](https://aka.ms/terminal) highly recommended on Windows):

```
$ fv1_programmer
```

This will bring up a user interface that will allow you to configure all 8 program slots of the Easy Spin's FV-1 DSP and write the EEPROM.

![image](https://github.com/audiofab/fv1_programmer/assets/1384978/36d8e9b9-4fe6-4cc4-b7b3-194910aaff97)

This utility was made possible by the amazing [Textual](https://textual.textualize.io/) project. Check it out!

This utility also leverages the excellent FV-1 assembler ([asfv1](https://github.com/ndf-zz/asfv1)) and disassembler ([disfv1](https://github.com/ndf-zz/disfv1)).
