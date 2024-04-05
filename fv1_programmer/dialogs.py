from textual.screen import ModalScreen

from textual import on
from textual.reactive import reactive
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Vertical
from textual.widgets import (
    Static,
    Button,
    DirectoryTree,
    Label,
    LoadingIndicator,
    Input,
)

from pathlib import Path
from typing import Iterable


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
    SUPPORTED_FILE_SUFFIXES = [".json", ".spn"]
    selection : reactive[Path | None] = reactive(None)

    def compose(self) -> ComposeResult:
        yield Grid(
            Static("Choose a file:", id="fileselectlabel"),
            FilteredDirectoryTree("./", id="filetree", valid_suffixes=LoadFileScreen.SUPPORTED_FILE_SUFFIXES),
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


class RenameSlotScreen(ModalScreen[str]):
    BINDINGS = [
        Binding("escape", "escape", "Exit the rename dialog"),
    ]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("New program slot name:"),
            Input("", id="newprogramslotname"),
            id="renameslotdialog",
        )

    def action_escape(self,):
        self.dismiss(None)

    @on(Input.Submitted)
    def accept_input(self,):
        self.dismiss(self.query_one("#newprogramslotname", Input).value)

