# FV-1 Programmer

An EEPROM programming tool for the FV-1 DSP.

# Installation

The easiest and cleanest way to install this demo is with [pipx](https://pypa.github.io/pipx/):

`pipx install fv1-programmer`

You can also install with pip (but it will install a bunch of dependencies directly into your Python environment):

`pip install fv1-programmer`

Either way, you will now have a `fv1_programmer` command on your path, which you can run in a terminal:

```
$ fv1_programmer
```

This will bring up a user interface that will allow you to configure all 8 program slots of the FV-1 DSP and write the EEPROM.
