# FV-1 Programmer

An EEPROM programming tool for the FV-1 DSP.

## Installation Instructions

### Dependencies

Install python 3.7 or grater

Install poetry

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

Add the installation folder to your `PATH`
```powershell
%APPDATA%\Python\Scripts
```

Restart your console.

Run 'poetry install`

### Running the program

`poetry run python main.py`
