# FV-1 Programmer

An EEPROM programming tool for the [Audiofab](https://audiofab.com/) [Easy Spin](https://audiofab.com/products/easy-spin) effects pedal.

# Installation

The easiest and cleanest way to install this demo is with [pipx](https://pypa.github.io/pipx/):

`pipx install fv1-programmer`

You can also install with pip (but it will install a bunch of dependencies directly into your Python environment):

`pip install fv1-programmer`

Either way, you will now have a `fv1_programmer` command on your path, which you can run in a terminal:

```
$ fv1_programmer
```

This will bring up a user interface that will allow you to configure all 8 program slots of the Easy Spin's FV-1 DSP and write the EEPROM.

![image](https://github.com/audiofab/fv1_programmer/assets/1384978/36d8e9b9-4fe6-4cc4-b7b3-194910aaff97)

This tool was made possible by the amazing [Textual](https://textual.textualize.io/) project. Check it out!

This tool also leverages the excellent FV-1 assembler ([asfv1](https://github.com/ndf-zz/asfv1)) and disassembler ([disfv1](https://github.com/ndf-zz/disfv1)).
