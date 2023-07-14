import argparse
# from pathlib import Path
# import sys


def parse_command_line_arguments():
    parser = argparse.ArgumentParser()
#     parser.add_argument('--programmer', default='MCP2221', choices=['MCP2221'],
#                         help='The type of programmer to use')
#     parser.add_argument('--i2c-address', default=0x50, type=lambda x: int(x, base=0),
#                         help='The I2C address of the target EEPROM')
#     parser.add_argument('--i2c-clock-speed', type=int, default=100000, choices=[47000, 100000, 400000],
#                         help='The I2C clock speed to use')
#     parser.add_argument('--ee-size', default=4096, type=int,
#                         help='The size (in bytes) of the EEPROM')
#     parser.add_argument('--ee-page-size', default=32, type=int,
#                         help='The EEPROM page size (in bytes)')
#     parser.add_argument('--pad-value', default=0xFF, type=lambda x: int(x, base=0) & 0xFF,
#                         help='The padding byte value (when loading a .hex file)')
#     parser.add_argument('--load-file', type=Path, default=None,
#                         help='If given, load the specified file (.hex or .bin) onto the device')
#     parser.add_argument('--save-file', type=Path, default=None,
#                         help='If given, read the entire contents of EEPROM and save to the specified file')
#     parser.add_argument('--verify', action="store_true", default=False,
#                         help='Verify the EEPROM contents after loading a .hex file')
    parser.add_argument('--debug', action="store_true", default=False,
                        help='Log debug messages')
#     parser.add_argument('--sim', type=Path, default=None,
#                         help='If specified, use the given file to emulate an EEPROM instead of a physical one')
    args = parser.parse_args()

    return args


# def __get_adapter(args):
#     if args.sim:
#         return None
#     elif args.programmer == 'MCP2221':
#         from adaptor.mcp2221 import MCP2221I2CAdaptor
#         return MCP2221I2CAdaptor(args.i2c_address, i2c_clock_speed=args.i2c_clock_speed)

#     raise ValueError(f"Unknown programmer {args.programmer}!")


# def __get_eeprom(args, adaptor):
#     if args.sim:
#         from eeprom.eeprom import DummyEEPROM
#         return DummyEEPROM(args.sim, args.ee_size)

#     from eeprom.eeprom import I2CEEPROM
#     return I2CEEPROM(adaptor, args.ee_size, page_size_in_bytes=args.ee_page_size)


# def save_file(args):
#     adaptor = __get_adapter(args)
#     if adaptor is not None:
#         adaptor.open()
#     ee = __get_eeprom(args, adaptor)
#     ee.save_file(args.save_file)
#     print(f"EEPROM content saved to '{str(args.save_file)}'")
#     return 0


# def load_file(args):
#     adaptor = __get_adapter(args)
#     if adaptor is not None:
#         adaptor.open()
#     ee = __get_eeprom(args, adaptor)
#     print(f"Loading{' (and verifying):' if args.verify else ':'} {str(args.load_file)}")
#     ee.load_file(args.load_file, padding=args.pad_value, verify=args.verify)
#     return 0

def run():
    args = parse_command_line_arguments()

    # if args.save_file is not None:
    #     sys.exit(save_file(args))

    # if args.load_file is not None:
    #     sys.exit(load_file(args))

    from fv1_programmer.tui import FV1App
    app = FV1App(args)
    app.run()


if __name__ == '__main__':
    run()
