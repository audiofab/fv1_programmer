from __future__ import annotations
import logging
import json
import re

from rich.console import RenderableType

from textual import on
from textual import work
from textual.reactive import reactive
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Grid, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen, ModalScreen
from textual.worker import Worker, get_current_worker
from textual.message import Message
from textual.widget import Widget
from textual.widgets import (
    Footer,
    Header,
    Static,
    TextLog,
    Button,
    TabbedContent,
    TabPane,
    Switch,
    Markdown,
    DirectoryTree,
    Tree,
    Label,
    LoadingIndicator,
    Input,
)

from typing import Iterable
from pathlib import Path
from fv1_programmer.fv1 import FV1Program, FV1_PROGRAM_MAX_BYTES
import pyperclip


__version__ = "0.2.8"

_title = "FV1 Programmer"

class BusyScreen(ModalScreen):
    def __init__(self, message : str) -> None:
        self.message = message
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(self.message),
            LoadingIndicator(),
            id="busyscreen"
        )


class FilteredDirectoryTree(DirectoryTree):
    def __init__(self, *args, **kwargs):
        self.valid_suffixes = []
        try:
            self.valid_suffixes = kwargs.pop("valid_suffixes")
        except KeyError:
            pass
        super().__init__(*args, **kwargs)

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if not path.name.startswith(".") and \
                    # TODO: Support SpinCAD file types as well!
                    path.is_dir() or (path.is_file() and path.suffix.lower() in self.valid_suffixes)]


class LoadFileScreen(ModalScreen[Path]):
    selection : reactive[Path | None] = reactive(None)

    def compose(self) -> ComposeResult:
        yield Grid(
            Static("Choose a file:", id="fileselectlabel"),
            FilteredDirectoryTree("./", id="filetree", valid_suffixes=[".json"]),
            Button("Cancel", variant="error", id="filedialogcancel"),
            Button("Select", variant="primary", id="filedialogselect"),
            id="filedialog",
        )

    @on(DirectoryTree.FileSelected, "#filetree")
    def do_file_selected(self, event : DirectoryTree.FileSelected):
        self.selection = event.path

    def watch_selection(self, new_path: Path):
        self.selection = new_path
        enabled = self.selection is not None
        select_button = self.query_one("#filedialogselect", Button)
        select_button.disabled = not enabled
        if enabled:
            select_button.focus()

    @on(Button.Pressed, "#filedialogselect")
    def do_select(self):
        self.dismiss(self.selection)

    @on(Button.Pressed, "#filedialogcancel")
    def cancel(self):
        self.dismiss(None)


class SaveFileScreen(ModalScreen[Path]):
    filename : reactive("")

    def compose(self) -> ComposeResult:
        yield Grid(
            Static("Please specify a filename:", id="fileselectlabel"),
            Input("my_programs", id="filesavefilename"),
            Button("Cancel", variant="error", id="filedialogcancel"),
            Button("Save", variant="primary", id="filedialogselect"),
            id="filesavedialog",
        )

    @on(Input.Changed)
    def check_filename(self, event: Input.Changed) -> None:
        self.query_one("#filedialogselect", Button).disabled = \
                    len(self.query_one("#filesavefilename", Input).value) < 1

    @on(Button.Pressed, "#filedialogselect")
    def do_save(self):
        self.dismiss(self.query_one("#filesavefilename", Input).value)

    @on(Button.Pressed, "#filedialogcancel")
    def cancel(self):
        self.dismiss(None)


class FV1ProgramPane(Widget):
    program : reactive[FV1Program | None] = reactive(None)

    def compose(self) -> ComposeResult:  
        yield Markdown()

    def watch_program(self, new_program: FV1Program):
        markdown = '# No program specified (leave this slot untouched)'
        if new_program is not None:
            markdown = new_program.as_markdown()

        self.query_one(Markdown).update(markdown)

    def on_mount(self) -> None:
        self.query_one(Markdown).tooltip = """Ctrl+C - Copy to clipboard\nCtrl+V/Ctrl+T - Paste from clipboard\nCtrl+D - Delete this program"""

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


class YesNoScreen(ModalScreen[bool]):
    def __init__(self, message, no_text="No", yes_text="Yes",
                 no_variant="primary", yes_variant="primary",
                 *args, **kwargs):
        self.message = message
        self.no_text = no_text
        self.yes_text = yes_text
        self.no_variant = no_variant
        self.yes_variant = yes_variant
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Grid(
            Static(self.message, id="yesnomessage"),
            Button(self.no_text, variant=self.no_variant, id="yesnono"),
            Button(self.yes_text, variant=self.yes_variant, id="yesnoyes"),
            id="yesnodialog",
        )

    @on(Button.Pressed, "#yesnoyes")
    def yes(self):
        self.dismiss(True)

    @on(Button.Pressed, "#yesnono")
    def no(self):
        self.dismiss(False)


class Title(Static):
    pass


class OptionSwitch(Horizontal):
    def __init__(self, name, label) -> None:
        self.option_name = name
        self.option_label = label
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Switch(value=getattr(self.app, self.option_name))
        yield Static(self.option_label, classes="label")

    def on_mount(self) -> None:
        self.watch(self.app, self.option_name, self.on_change, init=False)

    def on_change(self) -> None:
        self.query_one(Switch).value = getattr(self.app, self.option_name)

    def on_switch_changed(self, event: Switch.Changed) -> None:
        setattr(self.app, self.option_name, event.value)



class Sidebar(Container):
    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Title("Settings")
            yield OptionSwitch("setting_verify_writes", "Verify Writes")
            yield OptionSwitch("setting_asfv1_clamp", "Clamp Values (asfv1)")
            yield OptionSwitch("setting_asfv1_spinreals", "Spin Reals (asfv1)")
            yield OptionSwitch("setting_disfv1_relative", "Use Relative SKP Targets (disfv1)")
            yield OptionSwitch("setting_disfv1_suppressraw", "Convert Invalid Statements to NOP (disfv1)")


class ConsoleLogStream:
    def __init__(self, log_cb) -> None:
        self.log = log_cb
        self.name = "Console Log"

    def write(self, s):
        self.log(str(s).rstrip())


class MainScreen(Screen):
    TITLE = _title
    BINDINGS = [
        ("ctrl+l", "load_file", "Load"),
        ("ctrl+s", "save", "Save"),
        ("ctrl+r", "read_eeprom", "Read"),
        ("ctrl+w", "write_eeprom", "Write"),
        ("f1", "app.toggle_class('TextLog', '-hidden')", "Log"),
        ("f2", "toggle_sidebar", "Settings"),
        ("ctrl+q", "request_quit", "Quit"),
        Binding("ctrl+v", "paste", "Paste", show=False, priority=True),
        Binding("ctrl+t", "paste", "Paste", show=False, priority=True),
        Binding("ctrl+d", "delete", "Delete Program", show=False, priority=True),
    ]

    show_sidebar = reactive(False)

    class WriteEepromResult(Message):
        def __init__(self, programs : Iterable[dict], error=None) -> None:
            self.programs = programs
            self.error = error
            super().__init__()

    class ReadEepromResult(Message):
        def __init__(self, programs : Iterable[dict], error = None) -> None:
            self.programs = programs
            self.error = error
            super().__init__()

    def compose(self) -> ComposeResult:
        with Container():
            yield Sidebar(classes="-hidden")
            yield Header(show_clock=True)
            yield TextLog(id="consolelog", classes="-hidden", wrap=False, highlight=True, markup=True)
            yield ProgramTabs()
            yield Footer()

    def action_toggle_sidebar(self) -> None:
        sidebar = self.query_one(Sidebar)
        self.set_focus(None)
        if sidebar.has_class("-hidden"):
            sidebar.remove_class("-hidden")
        else:
            if sidebar.query("*:focus"):
                self.screen.set_focus(None)
            sidebar.add_class("-hidden")

    def console_log(self, renderable: RenderableType) -> None:
        self.query_one(TextLog).write(renderable)

    def on_mount(self) -> None:
        sh = logging.StreamHandler(stream=ConsoleLogStream(self.console_log))
        sh.setLevel(logging.INFO)
        self.app.logger.addHandler(sh)
        self.app.logger.info(f"FV1 Programmer version {__version__}")

    def action_request_quit(self,) -> None:
        def check_quit(should_quit : bool) -> None:
            if should_quit:
                self.app.do_exit()

        self.app.push_screen(YesNoScreen("Are you sure you want to quit?",
                                         yes_variant="error"), check_quit)

    def action_load_file(self) -> None:
        def handle_load_file(path : Path) -> None:
            if path is not None and path.exists() and path.is_file():
                with open(str(path), 'r') as f:
                    d = json.load(f)
                    programs = d.get("programs", [None]*8)
                    for i in range(1,9):
                        program_pane = self.query_one(f"#fv1prog{i}", FV1ProgramPane)
                        if programs[i - 1] is not None:
                            program_pane.program = FV1Program(programs[i - 1])
                self.app.show_toast(f"Loaded programs from {path}")

        self.app.push_screen(LoadFileScreen(), handle_load_file)

    def action_save(self) -> None:
        d = {"programs" : []}

        for i in range(1,9):
            program_pane = self.query_one(f"#fv1prog{i}", FV1ProgramPane)
            d["programs"].append(program_pane.program.asm if program_pane.program is not None else None)

        def handle_save_file(filename : str) -> None:
            def do_save_file(file_path):
                with open(file_path, 'w') as f:
                    json.dump(d, f, indent=2)
                    self.app.show_toast(f"Programs saved to {file_path}")

            if filename is not None:
                # Does filename already exist?
                save_path = Path(Path(".") / filename if filename.endswith(".json") else f"{filename}.json")
                if save_path.exists() and save_path.is_file():
                    def check_overwrite(should_overwrite : bool) -> None:
                        if should_overwrite:
                            do_save_file(save_path)
                    self.app.push_screen(YesNoScreen("File exists. Overwrite?"), check_overwrite)

                else:
                    do_save_file(save_path)

        self.app.push_screen(SaveFileScreen(), handle_save_file)

    def action_write_eeprom(self) -> None:
        programs = []
        for i in range(1,9):
            program_pane = self.query_one(f"#fv1prog{i}", FV1ProgramPane)
            if program_pane.program is not None:
                bin_array, warnings, errors = program_pane.program.assemble(
                                                            clamp=self.app.setting_asfv1_clamp,
                                                            spinreals=self.app.setting_asfv1_spinreals)
                programs.append({"program": i, "address" : (i - 1)*FV1_PROGRAM_MAX_BYTES, "data" : bin_array})
        if len(programs) == 0:
            self.app.show_toast("Nothing to do!", severity="warning")
        else:
            self.app.push_screen(BusyScreen("Downloading to pedal..."))
            self.write_eeprom(programs, self.app.setting_simulate)

    def _get_eeprom(self,):
        if self.app.setting_simulate:
            from eeprom.eeprom import DummyEEPROM
            return DummyEEPROM(Path(self.app.cmdline_args.sim), self.app.cmdline_args.ee_size)
        else:
            from adaptor.mcp2221 import MCP2221I2CAdaptor
            from eeprom.eeprom import I2CEEPROM
            adaptor = MCP2221I2CAdaptor(self.app.cmdline_args.i2c_address,
                                        i2c_clock_speed=self.app.cmdline_args.i2c_clock_speed)
            adaptor.open()
            return I2CEEPROM(adaptor, self.app.cmdline_args.ee_size,
                             page_size_in_bytes=self.app.cmdline_args.ee_page_size)

    @work(exclusive=True)
    def write_eeprom(self, programs : Iterable[dict], simulate : bool) -> None:
        worker = get_current_worker()
        eeprom = None
        try:
            eeprom = self._get_eeprom()
        except Exception as e:
            if not worker.is_cancelled:
                self.post_message(self.WriteEepromResult(programs, error=e))

        if eeprom is not None:
            for program in programs:
                addr = program["address"]
                data = program["data"]
                eeprom.write_bytes(addr, data)

            error = None
            # Read back all the data and verify
            if self.app.setting_verify_writes:
                for program in programs:
                    addr = program["address"]
                    data = program["data"]
                    read_data = eeprom.read_bytes(addr, len(data))
                    if read_data != data:
                        error = ValueError("EEPROM write failed verification!")
                        break

            if not worker.is_cancelled:
                self.post_message(self.WriteEepromResult(programs, error=error))

    def on_main_screen_write_eeprom_result(self, message : MainScreen.WriteEepromResult) -> None:
        """Called when a write eeprom operation is finished."""
        self.app.pop_screen()
        if message.error is not None:
            self.app.logger.error(str(message.error))
            self.app.show_toast("EEPROM write failed! See log for details.", title="Error", severity="error")
        else:
            # total_bytes = sum([len(w["data"]) for w in message.programs])
            self.app.show_toast(f"Wrote to program slots {[w['program'] for w in message.programs]}{' (simulation)' if self.app.setting_simulate else ''}")
            if self.app.setting_verify_writes:
                self.app.logger.info("All programs verified successfully.")

    def action_read_eeprom(self) -> None:
        def do_read_eeprom():
            self.app.push_screen(BusyScreen("Reading from pedal..."))
            self.read_eeprom(self.app.setting_simulate,
                             self.app.setting_disfv1_relative,
                             self.app.setting_disfv1_suppressraw)

        num_programs = 0
        for i in range(1,9):
            program_pane = self.query_one(f"#fv1prog{i}", FV1ProgramPane)
            if program_pane.program is not None:
                num_programs += 1

        if num_programs > 0:
            # Ask the user if they want to overwrite their current programs
            def check_overwrite(should_overwrite : bool) -> None:
                if should_overwrite:
                    do_read_eeprom()
            self.app.push_screen(YesNoScreen("This will overwrite your current programs.\nAre you sure?"), check_overwrite)

        else:
            do_read_eeprom()

    @work(exclusive=True)
    def read_eeprom(self, simulate : bool, relative : bool, suppressraw : bool) -> None:
        worker = get_current_worker()
        eeprom = None
        try:
            eeprom = self._get_eeprom()
        except Exception as e:
            if not worker.is_cancelled:
                self.post_message(self.ReadEepromResult({}, error=e))

        if eeprom is not None:
            programs = []
            program_data = eeprom.read_bytes(0, FV1_PROGRAM_MAX_BYTES*8)
            for offset in range(0, 8*FV1_PROGRAM_MAX_BYTES, FV1_PROGRAM_MAX_BYTES):
                program = FV1Program("")
                warnings = program.from_bytearray(program_data[offset:offset + FV1_PROGRAM_MAX_BYTES],
                                                  relative=relative, suppressraw=suppressraw)
                programs.append({"program" : program, "warnings" : warnings})

            if not worker.is_cancelled:
                self.post_message(self.ReadEepromResult(programs))

    def on_main_screen_read_eeprom_result(self, message : MainScreen.ReadEepromResult) -> None:
        """Called when a read eeprom operation is finished."""
        self.app.pop_screen()
        if message.error is not None:
            self.app.logger.error(str(message.error))
            self.app.show_toast("EEPROM read failed! See log for details.", title="Error", severity="error")
            return

        were_warnings = False
        for i in range(1,9):
            program_pane = self.query_one(f"#fv1prog{i}", FV1ProgramPane)
            program_pane.program = message.programs[i - 1]["program"]
            warnings = message.programs[i - 1]["warnings"]
            if warnings is not None:
                for warning in warnings:
                    self.app.logger.info(warning)
                    m = re.match("info: Read (\d+) instructions\.", warning)
                    # Only worry about real warnings
                    if m.group(0) != warning:
                        were_warnings = True

        if were_warnings:
            self.app.show_toast("EEPROM read succeeded with warnings. See log for details.", title="Warning", severity="warning")
        else:
            self.app.show_toast("EEPROM read complete.")

    def action_paste(self) -> None:
        # Validate program
        new_program = FV1Program(pyperclip.paste())
        bin_array, warnings, errors = new_program.assemble(clamp=self.app.setting_asfv1_clamp,
                                                           spinreals=self.app.setting_asfv1_spinreals)
        [self.app.logger.info(w) for w in warnings]
        [self.app.logger.info(e) for e in errors]
        if len(errors) == 0:
            active_program_pane = self.query_one(f"#fv1{self.query_one(TabbedContent).active}", FV1ProgramPane)
            active_program_pane.program = FV1Program(pyperclip.paste())
        else:
            self.app.show_toast("Ignoring invalid clipboard contents. See log for details.")

    def action_delete(self) -> None:
        active_program_pane = self.query_one(f"#fv1{self.query_one(TabbedContent).active}", FV1ProgramPane)
        active_program_pane.program = None


from dataclasses import dataclass
@dataclass
class Args:
    """Class emulating command line arguments to allow running via `textual run --dev`"""
    i2c_addr:int
    i2c_clock_speed:int
    ee_size:int
    ee_page_size:int
    pad_value:int
    verify:bool
    debug:bool
    sim:Path


class FV1App(App[None]):
    CSS_PATH = "tui.css"
    SCREENS = {"main" : MainScreen()}

    def __init__(self, cmdline_args=None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.cmdline_args = cmdline_args

        # See if we're being run by `textual run --dev`
        if 'devtools' in self.features:
            self.cmdline_args = Args(0x50,
                                     100000,
                                     4096,
                                     32,
                                     0xFF,
                                     True,
                                     False,
                                     Path('backup.bin'))

        # Whether to use a programmer or just simulate
        self.setting_simulate = self.cmdline_args.sim is not None
        self.setting_verify_writes = self.cmdline_args.verify

        # asfv1 options
        self.setting_asfv1_clamp = True
        self.setting_asfv1_spinreals = False

        # disfv1 options
        self.setting_disfv1_relative = False
        self.setting_disfv1_suppressraw = False

        self.logger = logging.getLogger("FV1App")
        # Avoid all output being sent to the console as well
        self.logger.propagate = False
        self.logger.setLevel(logging.DEBUG if self.cmdline_args.debug else logging.INFO)
        if self.cmdline_args.debug:
            fh = logging.FileHandler('app_debug.log', encoding='utf-8', mode='w')
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
            self.logger.addHandler(fh)

    # Intercept the app exit (the only thing connected to this should be Ctrl+C)
    # and make it behave like Copy
    def exit(self, result = None) -> None:
        active_program_pane = self.query_one(f"#fv1{self.query_one(TabbedContent).active}", FV1ProgramPane)
        if active_program_pane.program is not None:
            pyperclip.copy(active_program_pane.program.asm)
            self.show_toast("Current program copied to clipboard")

    def do_exit(self, result = None) -> None:
        super().exit(result)

    def on_mount(self) -> None:
        self.push_screen("main")

    def show_toast(self, message, title=None, severity="information", timeout=4.0) -> None:
        self.logger.info(message)
        self.notify(message, title=title, severity=severity, timeout=timeout)
