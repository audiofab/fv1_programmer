import argparse
import pathlib
import os

def parse_command_line_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level', choices=['INFO', 'WARN', 'DEBUG', 'ERROR'],
                        default='INFO',
                        help=f'The logging level')
    parser.add_argument('--port', default='COM3',
                        help='The COM port to use')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_command_line_arguments()

    # from tui import DemoApp

    # app = DemoApp(args)
    # app.run()

    # print(args)