from __future__ import annotations
import logging

from rich.console import RenderableType

from textual import on
from textual.reactive import reactive
from textual.app import App, ComposeResult
from textual.containers import Container, Grid
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import (
    Footer,
    Header,
    Static,
    TextLog,
    Button,
    TabbedContent,
    TabPane,
    Markdown,
)


from pathlib import Path
from fv1_programmer.fv1 import EMPTY_FV1_PROGRAM, ROM_REV1


__version__ = "0.1.0"

_title = "FV1 Programmer"


class FV1ProgramPane(Widget):
    program = reactive(EMPTY_FV1_PROGRAM)

    def compose(self) -> ComposeResult:  
        yield Markdown()

    def watch_program(self, new_program: str):
        self.query_one(Markdown).update(f"```{new_program}```")


class ProgramTabs(Widget):
    def compose(self) -> ComposeResult:  
        with TabbedContent():
            with TabPane("Program 1", id="prog1"):
                yield FV1ProgramPane(id="fv1prog1")
            with TabPane("Program 2", id="prog2"):
                yield FV1ProgramPane(id="fv1prog2")
            with TabPane("Program 3", id="prog3"):
                yield FV1ProgramPane(id="fv1prog3")
            with TabPane("Program 4", id="prog4"):
                yield FV1ProgramPane(id="fv1prog4")
            with TabPane("Program 5", id="prog5"):
                yield FV1ProgramPane(id="fv1prog5")
            with TabPane("Program 6", id="prog6"):
                yield FV1ProgramPane(id="fv1prog6")
            with TabPane("Program 7", id="prog7"):
                yield FV1ProgramPane(id="fv1prog7")
            with TabPane("Program 8", id="prog8"):
                yield FV1ProgramPane(id="fv1prog8")


class QuitScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Grid(
            Static("Are you sure you want to quit?", id="question"),
            Button("Quit", variant="error", id="quit"),
            Button("Cancel", variant="primary", id="cancel"),
            id="quitdialog",
        )

    @on(Button.Pressed, "#quit")
    def quit(self):
        self.app.do_exit()

    @on(Button.Pressed, "#cancel")
    def cancel(self):
        self.app.pop_screen()

class ConsoleLogStream:
    def __init__(self, log_cb) -> None:
        self.log = log_cb
        self.name = "Console Log"

    def write(self, s):
        self.log(str(s).rstrip())


class MainScreen(Screen):
    TITLE = _title
    BINDINGS = [
        ("ctrl+l", "load_file", "Load File"),
        ("ctrl+r", "read_eeprom", "Read EEPROM"),
        ("ctrl+w", "write_eeprom", "Write EEPROM"),
        ("f1", "app.toggle_class('TextLog', '-hidden')", "Show Log"),
        ("ctrl+q", "request_quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        with Container():
            yield Header(show_clock=True)
            yield TextLog(id="consolelog", classes="-hidden", wrap=False, highlight=True, markup=True)
            yield ProgramTabs()
            yield Footer()

    def console_log(self, renderable: RenderableType) -> None:
        self.query_one(TextLog).write(renderable)

    def on_mount(self) -> None:
        sh = logging.StreamHandler(stream=ConsoleLogStream(self.console_log))
        sh.setLevel(logging.INFO)
        self.app.logger.addHandler(sh)
        self.app.logger.info(f"FV1 Programmer version {__version__}")

    def action_request_quit(self) -> None:
        self.app.push_screen("quit")

    def action_load_file(self) -> None:
        active_program = self.query_one(f"#fv1{self.query_one(TabbedContent).active}", FV1ProgramPane)
        active_program.program = ROM_REV1

    def action_read_eeprom(self) -> None:
        self.app.logger.info("Read EEPROM (Not Implemented)")

    def action_write_eeprom(self) -> None:
        self.app.logger.info("Write EEPROM (Not Implemented)")


    # @on(ScreenResume)
    # def update_device_info(self):
    #     self.app.logger.debug(f"Using the following devices: [{self.app.left_device}, {self.app.right_device}]")
    #     self.query_one('#deviceleft').device_info = self.app.left_device
    #     self.query_one('#deviceright').device_info = self.app.right_device



from dataclasses import dataclass
@dataclass
class Args:
    """Class emulating command line arguments to allow running via `textual run --dev`"""
    programmer:str
    i2c_addr:int
    i2c_clock_speed:int
    ee_size:int
    ee_page_size:int
    pad_value:int
    load_File:Path
    save_File:Path
    verify:bool
    debug:bool
    sim:bool

class FV1App(App[None]):
    CSS_PATH = "tui.css"
    SCREENS = {"main" : MainScreen(), "quit" : QuitScreen()}

    def __init__(self, cmdline_args=None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.cmdline_args = cmdline_args

        # See if we're being run by `textual run --dev`
        if 'devtools' in self.features:
            self.cmdline_args = Args('MCP2221',
                                     0x50,
                                     100000,
                                     4096,
                                     32,
                                     0xFF,
                                     None,
                                     None,
                                     True,
                                     False,
                                     True)

        self.logger = logging.getLogger("FV1App")
        # Avoid all output being sent to the console as well
        self.logger.propagate = False
        self.logger.setLevel(logging.DEBUG if self.cmdline_args.debug else logging.INFO)
        if self.cmdline_args.debug:
            fh = logging.FileHandler('app_debug.log', encoding='utf-8', mode='w')
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
            self.logger.addHandler(fh)

        self.EEPROM = None


    def on_mount(self) -> None:
        self.push_screen("main")

    def exit(self, result = None) -> None:
        self.push_screen("quit")

    def do_exit(self, result = None) -> None:
        super().exit(result)
