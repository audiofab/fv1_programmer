import argparse
from pathlib import Path
import sys


def parse_command_line_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--programmer', default='MCP2221', choices=['MCP2221', 'CH341'],
                        help='The type of programmer to use')
    parser.add_argument('--i2c-address', default=0x50, type=lambda x: int(x, base=0),
                        help='The I2C address of the target EEPROM')
    parser.add_argument('--i2c-clock-speed', type=int, default=100000, choices=[47000, 100000, 400000],
                        help='The I2C clock speed to use')
    parser.add_argument('--ee-size', default=4096, type=int,
                        help='The size (in bytes) of the EEPROM')
    parser.add_argument('--ee-page-size', default=32, type=int,
                        help='The EEPROM page size (in bytes)')
    parser.add_argument('--pad-value', default=0xFF, type=lambda x: int(x, base=0) & 0xFF,
                        help='The padding byte value (when loading a .hex file)')
    parser.add_argument('--load-file', type=Path, default=None,
                        help='If given, load the specified file (.hex or .bin) onto the device')
    parser.add_argument('--save-file', type=Path, default=None,
                        help='If given, read the entire contents of EEPROM and save to the specified file')
    parser.add_argument('--verify', action="store_true", default=False,
                        help='Verify the EEPROM contents after loading a .hex file')
    args = parser.parse_args()

    if args.programmer == 'CH341':
        raise ValueError("CH341 programmer support is not implemented.")

    return args


def save_file(args):
    from adaptor.mcp2221 import MCP2221I2CAdaptor
    from eeprom.eeprom import I2CEEPROM

    adaptor = MCP2221I2CAdaptor(args.i2c_address, i2c_clock_speed=args.i2c_clock_speed)
    adaptor.open()
    ee = I2CEEPROM(adaptor, size_in_bytes=args.ee_size, page_size_in_bytes=args.ee_page_size)
    ee.save_file(args.save_file)
    print(f"EEPROM content saved to '{str(args.save_file)}'")
    return 0


def load_file(args):
    from adaptor.mcp2221 import MCP2221I2CAdaptor
    from eeprom.eeprom import I2CEEPROM

    adaptor = MCP2221I2CAdaptor(args.i2c_address, i2c_clock_speed=args.i2c_clock_speed)
    adaptor.open()
    ee = I2CEEPROM(adaptor, size_in_bytes=args.ee_size, page_size_in_bytes=args.ee_page_size)
    print(f"Loading{' (and verifying):' if args.verify else ':'} {str(args.load_file)}")
    ee.load_file(args.load_file, padding=args.pad_value, verify=args.verify)
    return 0

def run():
    args = parse_command_line_arguments()

    if args.save_file is not None:
        sys.exit(save_file(args))

    if args.load_file is not None:
        sys.exit(load_file(args))

    # from tui import DemoApp
    # app = DemoApp(args)
    # app.run()


if __name__ == '__main__':
    run()
