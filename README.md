# FV-1 Programmer

An EEPROM programming tool for the FV-1 DSP.

# Installation

The easiest and cleanest way to install this demo is with [pipx](https://pypa.github.io/pipx/):

`pipx install fv1-programmer`

You can also install with pip (but it will install a bunch of dependencies directly into your Python environment):

`pip install fv1-programmer`

Either way, you will now have a `fv1_programmer` command on your path, which you can run in a terminal:

```
$ fv1_programmer -h
usage: fv1_programmer [-h] [--programmer {MCP2221,CH341}] [--i2c-address I2C_ADDRESS]
                      [--i2c-clock-speed {47000,100000,400000}] [--ee-size EE_SIZE] [--ee-page-size EE_PAGE_SIZE]
                      [--pad-value PAD_VALUE] [--load-file LOAD_FILE] [--save-file SAVE_FILE] [--verify]

optional arguments:
  -h, --help            show this help message and exit
  --programmer {MCP2221,CH341}
                        The type of programmer to use
  --i2c-address I2C_ADDRESS
                        The I2C address of the target EEPROM
  --i2c-clock-speed {47000,100000,400000}
                        The I2C clock speed to use
  --ee-size EE_SIZE     The size (in bytes) of the EEPROM
  --ee-page-size EE_PAGE_SIZE
                        The EEPROM page size (in bytes)
  --pad-value PAD_VALUE
                        The padding byte value (when loading a .hex file)
  --load-file LOAD_FILE
                        If given, load the specified file (.hex or .bin) onto the device
  --save-file SAVE_FILE
                        If given, read the entire contents of EEPROM and save to the specified file
  --verify              Verify the EEPROM contents after loading a .hex file
```
