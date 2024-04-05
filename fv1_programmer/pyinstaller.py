import PyInstaller.__main__
from pathlib import Path

this_dir = Path(__file__).parent.absolute()
path_to_main = str(this_dir / "main.py")

def make_exe():
    PyInstaller.__main__.run([
        path_to_main,
        '--onefile',
        '--clean',
        '--console',
        '--name', 'fv1_programmer',
        '--add-data', f'{str(this_dir / "tui.css")}:fv1_programmer',
        '--add-data', f'{str(this_dir / "dialogs.css")}:fv1_programmer',
        '--paths', str(this_dir / ".."),
        '--version-file', str(this_dir / "../version.rc"),
        '--icon', str(this_dir / "../audiofab.ico"),
        '--hidden-import', "textual.widgets._tab_pane",
        '--collect-submodules', "asfv1",
        '--collect-submodules', "disfv1",
        '--collect-submodules', "eeprom",
        '--collect-submodules', "adapter",
    ])

if __name__ == '__main__':
    make_exe()
