from __future__ import annotations
import logging
import json
import re
import os
import shlex

from rich.console import RenderableType

from textual import events, on
from textual import work
from textual.reactive import reactive
from textual.app import App, ComposeResult
from textual.command import Hit, Hits, DiscoveryHit, Provider, CommandPalette
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.worker import get_current_worker
from textual.message import Message
from textual.widget import Widget
from textual.widgets import (
    Footer,
    Header,
    Static,
    RichLog,
    TabbedContent,
    TabPane,
    Switch,
    DirectoryTree,
    TextArea,
    ContentSwitcher,
    Markdown,
)

from functools import partial
from typing import Iterable
from pathlib import Path
import pyperclip
from fv1_programmer.fv1 import FV1Program, FV1_PROGRAM_MAX_BYTES
from fv1_programmer.dialogs import *


__version__ = "0.5.1"

_title = "FV1 Programmer"
MIN_PROGRAM_NUM = 1
MAX_PROGRAM_NUM = 8

class FV1AppCommands(Provider):
    """A command provider to open a Python file in the current working directory."""

    async def startup(self) -> None:
        """Called once when the command palette is opened"""
        self.discovery_commands = [
            ("Rename current program", self.screen.action_rename_program_slot, "Provide your own name for this program slot"),
            ("New program", self.screen.action_new, "Create a new, empty program in current slot (Ctr+N)"),
            ("Delete current program", self.screen.action_delete,"Delete any program in current slot"),
        ]

    async def discover(self,) -> Hits:
        for name, callback, help_msg in self.discovery_commands:
            yield DiscoveryHit(name, callback, help=help_msg)

    async def search(self, query: str) -> Hits:
        """Search for Python files."""
        matcher = self.matcher(query)  

        app = self.app
        assert isinstance(app, FV1App)

        # Slot swapping commands
        for i in range(MIN_PROGRAM_NUM, MAX_PROGRAM_NUM + 1):
            command = f"Swap with slot {i}"
            score = matcher.match(command)
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(command),
                    partial(self.screen.swap_with_slot, i),
                    help=f"Swap this slot with slot {i}",
                )


class FV1ProgramPane(Widget):
    program : reactive[FV1Program | None] = reactive(None)

    def compose(self) -> ComposeResult:
        with ContentSwitcher(initial="empty-slot"):  
            yield Markdown(id="empty-slot")
            yield TextArea.code_editor("", id="text-area-slot")

    def watch_program(self, new_program: FV1Program):
        if new_program is not None:
            self.query_one(ContentSwitcher).current = "text-area-slot"
            self.query_one(TextArea).text = new_program.assembly
        else:
            self.query_one(ContentSwitcher).current = "empty-slot"

    def on_mount(self) -> None:
        self.query_one(Markdown).update("""# Empty Program Slot
This is an empty program slot that will be ignored when downloading to the Easy Spin pedal. <br>

To add a program to this slot, you can do one of the following:

- Click here or press Ctrl+N to [create a new program for editing](#new-program)
- Drag and drop an appropriate file onto this window (.spn, .json)

Press *Ctrl+D* to delete a program and reset the program slot to be empty (ignored during download) <br>

Also see these helpful links: <br>

Textual documentation for the editor keybindings: https://textual.textualize.io/widgets/text_area/#bindings <br>
Easy Spin webpage: https://audiofab.com/products/easy-spin <br>
""")

    @on(Markdown.LinkClicked)
    def on_click(self, event):
        if event.href == "#new-program":
            self.program = FV1Program("")

    @on(TextArea.Changed)
    def on_changed(self, event):
        self.program.asm = self.query_one(TextArea).text
        self.query_one(TextArea).focus()


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

    # @on(TabbedContent.TabActivated)
    # def on_tab_changed(self, event):
    #     self.app.logger.info(event.pane.query_one(TextArea))
    #     event.pane.query_one(TextArea).focus()

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
        Binding("ctrl+n", "new", "New Program", show=False, priority=True),
        Binding("ctrl+p", "command_palette", show=False, priority=True),
        Binding("ctrl+l", "load_file", "Load", priority=True),
        Binding("ctrl+s", "save", "Save", priority=True),
        Binding("ctrl+r", "read_eeprom", "Read", priority=True),
        Binding("ctrl+w", "write_eeprom", "Write", priority=True),
        ("f1", "app.toggle_class('RichLog', '-hidden')", "Log"),
        ("f2", "toggle_sidebar", "Settings"),
        ("ctrl+q", "request_quit", "Quit"),
    ]
    COMMANDS = {FV1AppCommands}

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
            yield RichLog(id="consolelog", classes="-hidden", wrap=False, highlight=True, markup=True)
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
        self.query_one(RichLog).write(renderable)

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

    def action_command_palette(self) -> None:
        """Show the Textual command palette."""
        if not CommandPalette.is_open(self):
            self.app.push_screen(CommandPalette(), callback=self.app.call_next)

    def swap_with_slot(self, dest_slot : int) -> None:
        """Swaps the current program slot with `dest_slot`"""
        active_tab_id = self.query_one(TabbedContent).active
        active_slot = active_tab_id.split("prog")[1]
        if active_slot == dest_slot:
            return
        active_program_pane = self.query_one(f"#fv1{self.query_one(TabbedContent).active}", FV1ProgramPane)
        dest_program_pane = self.query_one(f"#fv1prog{dest_slot}", FV1ProgramPane)
        tmp_prog = dest_program_pane.program
        dest_program_pane.program = active_program_pane.program
        active_program_pane.program = tmp_prog

        active_name = self.query_one(TabbedContent).get_tab(f"{self.query_one(TabbedContent).active}").label
        dest_name = self.query_one(TabbedContent).get_tab(f"prog{dest_slot}").label
        self.rename_program_slot(active_slot, dest_name)
        self.rename_program_slot(dest_slot, active_name)

    def rename_program_slot(self, slot_num : int, name : str) -> None:
        self.query_one(TabbedContent).get_tab(f"prog{slot_num}").label = name

    def action_rename_program_slot(self,) -> None:
        """Prompts the user for a name for the current program slot"""
        def handle_program_rename(name : str) -> None:
            if name and len(name):
                self.rename_program_slot(self.query_one(TabbedContent).active.split("prog")[1], name)

        self.app.push_screen(RenameSlotScreen(), handle_program_rename)

    def load_json_file(self, path : Path) -> None:
        with open(str(path), 'r') as f:
            d = json.load(f)
            programs = d.get("programs", [None]*8)
            for i in range(MIN_PROGRAM_NUM, MAX_PROGRAM_NUM + 1):
                program_pane = self.query_one(f"#fv1prog{i}", FV1ProgramPane)
                if programs[i - 1] is not None:
                    if isinstance(programs[i - 1], str):
                        program_pane.program = FV1Program(programs[i - 1])
                        self.rename_program_slot(i, f"Program {i}")
                    else:
                        self.rename_program_slot(i, programs[i - 1].get("name", f"Program {i}"))
                        prog = programs[i - 1].get("asm", None)
                        program_pane.program = FV1Program(prog) if prog is not None else prog

        self.app.show_toast(f"Loaded programs from {path}")

    def load_spn_file(self, path : Path, slot_number : int) -> None:
        with open(str(path), 'r') as f:
            program_pane = self.query_one(f"#fv1prog{slot_number}", FV1ProgramPane)
            program_pane.program = FV1Program("".join(f.readlines()))
            self.rename_program_slot(slot_number, path.stem)
        self.app.show_toast(f"Loaded {path}")

    def handle_load_file(self, path : Path) -> None:
        if path is not None and path.exists() and path.is_file():
            if path.suffix.lower() == ".json":
                self.load_json_file(path)
            elif path.suffix.lower() == ".spn":
                active_tab_id = self.query_one(TabbedContent).active
                active_slot = active_tab_id.split("prog")[1]
                self.load_spn_file(path, active_slot)

    def action_load_file(self) -> None:
        self.app.push_screen(LoadFileScreen(), self.handle_load_file)

    def on_paste(self, event: events.Paste) -> None:
        event.stop()

        # Detect file drop
        def _extract_filepaths(text: str) -> list[str]:
            """Extracts escaped filepaths from text.
            
            Taken from https://github.com/agmmnn/textual-filedrop/blob/55a288df65d1397b959d55ef429e5282a0bb21ff/textual_filedrop/_filedrop.py#L17-L36
            """
            split_filepaths = []
            if os.name == "nt":
                pattern = r'(?:[^\s"]|"(?:\\"|[^"])*")+'
                split_filepaths = re.findall(pattern, text)
            else:
                split_filepaths = shlex.split(text)

            filepaths: list[Path] = []
            for i in split_filepaths:
                item = Path(i.replace("\x00", "").replace('"', ""))
                if item.is_file():
                    filepaths.append(item)
            return filepaths
        
        try:
            filepaths = _extract_filepaths(event.text)
            if filepaths and len(filepaths) > 0:
                # To keep things simple for now, we only support
                # dropping a single file
                self.handle_load_file(filepaths[0])

        except ValueError:
            pass

    def action_save(self) -> None:
        d = {"programs" : []}

        for i in range(MIN_PROGRAM_NUM, MAX_PROGRAM_NUM + 1):
            program_pane = self.query_one(f"#fv1prog{i}", FV1ProgramPane)
            prog_d = {}
            prog_d["asm"] = program_pane.program.asm if program_pane.program is not None else None
            prog_d["name"] = str(self.query_one(TabbedContent).get_tab(f"prog{i}").label)
            d["programs"].append(prog_d)

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
        errors = 0
        for i in range(MIN_PROGRAM_NUM, MAX_PROGRAM_NUM + 1):
            program_pane = self.query_one(f"#fv1prog{i}", FV1ProgramPane)
            if program_pane.program is not None:
                bin_array = self.assemble_and_validate_program(program_pane.program)
                if bin_array is not None:
                    if len(bin_array):
                        programs.append({"program": i, "address" : (i - 1)*FV1_PROGRAM_MAX_BYTES, "data" : bin_array})
                    else:
                        # Program assembled but there are no instructions
                        self.app.show_toast(f"Program {i} has no instructions.")
                else:
                    self.app.show_toast(f"Program {i} failed to assemble. See log for details.")
                    errors += 1

        if errors > 0:
            self.app.show_toast("Errors while assembling. Download aborted.", severity="warning")
        else:
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

    @work(exclusive=True, thread=True)
    def write_eeprom(self, programs : Iterable[dict], simulate : bool) -> None:
        worker = get_current_worker()
        eeprom = None
        error = None
        try:
            eeprom = self._get_eeprom()

            if eeprom is not None:
                for program in programs:
                    addr = program["address"]
                    data = program["data"]
                    eeprom.write_bytes(addr, data)

                # Read back all the data and verify
                if self.app.setting_verify_writes:
                    for program in programs:
                        addr = program["address"]
                        data = program["data"]
                        read_data = eeprom.read_bytes(addr, len(data))
                        if read_data != data:
                            error = ValueError("EEPROM write failed verification!")
                            break
        except Exception as e:
            if not worker.is_cancelled:
                self.post_message(self.WriteEepromResult(programs, error=e))
        else:
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
        for i in range(MIN_PROGRAM_NUM, MAX_PROGRAM_NUM + 1):
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

    @work(exclusive=True, thread=True)
    def read_eeprom(self, simulate : bool, relative : bool, suppressraw : bool) -> None:
        worker = get_current_worker()
        eeprom = None
        try:
            eeprom = self._get_eeprom()

            if eeprom is not None:
                programs = []
                program_data = eeprom.read_bytes(0, FV1_PROGRAM_MAX_BYTES*8)
                for offset in range(0, 8*FV1_PROGRAM_MAX_BYTES, FV1_PROGRAM_MAX_BYTES):
                    program = FV1Program("")
                    warnings = program.from_bytearray(program_data[offset:offset + FV1_PROGRAM_MAX_BYTES],
                                                    relative=relative, suppressraw=suppressraw)
                    programs.append({"program" : program, "warnings" : warnings})

        except Exception as e:
            if not worker.is_cancelled:
                self.post_message(self.ReadEepromResult({}, error=e))
        else:
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
        for i in range(MIN_PROGRAM_NUM, MAX_PROGRAM_NUM + 1):
            program_pane = self.query_one(f"#fv1prog{i}", FV1ProgramPane)
            program_pane.program = message.programs[i - 1]["program"]
            warnings = message.programs[i - 1]["warnings"]
            if warnings is not None:
                for warning in warnings:
                    self.app.logger.info(warning)
                    m = re.match(r"info: Read (\d+) instructions\.", warning)
                    # Only worry about real warnings
                    if m.group(0) != warning:
                        were_warnings = True

        if were_warnings:
            self.app.show_toast("EEPROM read succeeded with warnings. See log for details.", title="Warning", severity="warning")
        else:
            self.app.show_toast("EEPROM read complete.")

    def action_delete(self) -> None:
        active_tab_id = self.query_one(TabbedContent).active
        active_slot = active_tab_id.split("prog")[1]
        active_program_pane = self.query_one(f"#fv1{active_tab_id}", FV1ProgramPane)
        active_program_pane.program = None
        self.rename_program_slot(active_slot, f"Program {active_slot}")

    def action_new(self) -> None:
        active_tab_id = self.query_one(TabbedContent).active
        active_slot = active_tab_id.split("prog")[1]
        active_program_pane = self.query_one(f"#fv1{active_tab_id}", FV1ProgramPane)
        active_program_pane.program = FV1Program("")
        self.rename_program_slot(active_slot, f"Program {active_slot}")
        active_program_pane.query_one(TextArea).focus()

    def assemble_and_validate_program(self, program) -> bytearray:
        bin_array, num_instructions, warnings, errors = program.assemble(clamp=self.app.setting_asfv1_clamp,
                                                                         spinreals=self.app.setting_asfv1_spinreals)
        [self.app.logger.info(w) for w in warnings]
        [self.app.logger.info(e) for e in errors]
        if len(errors) == 0:
            if num_instructions > 0:
                return bin_array
            else:
                return []
        return None


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
    CSS_PATH = ["tui.css", "dialogs.css"]
    SCREENS = {"main" : MainScreen()}
    ENABLE_COMMAND_PALETTE = False
    COMMANDS = {}

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
        self.setting_asfv1_spinreals = True

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
            pyperclip.copy(active_program_pane.query_one(TextArea).selected_text)
        #     self.show_toast("Current program copied to clipboard")

    def do_exit(self, result = None) -> None:
        super().exit(result)

    def on_mount(self) -> None:
        self.push_screen("main")

    def show_toast(self, message, title=None, severity="information", timeout=4.0) -> None:
        self.notify(message, title=title, severity=severity, timeout=timeout)
