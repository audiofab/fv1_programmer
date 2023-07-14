from asfv1.asfv1 import fv1parse, ASFV1Error
from typing import Tuple


EMPTY_FV1_PROGRAM_ASM = """
; Empty program

start:
    NOP
end:
    NOP
"""

class FV1Program(object):
    def __init__(self, asm) -> None:
        self.asm = asm

    def assemble(self, clamp=True, spinreals=False) -> Tuple[bytearray, str, str]:
 
        warnings = []
        errors = []

        def warning(msg):
            nonlocal warnings
            warnings.append(msg)

        def error(msg):
            nonlocal errors
            errors.append(msg)

        fp = fv1parse(self.asm,
                      clamp=clamp, spinreals=spinreals,
                      wfunc=warning, efunc=error)
        try:
            fp.parse()
        except ASFV1Error:
            if len(errors) == 0:
                errors = ["Failed to assemble program"]
            return None, warnings, errors

        return fp.program, warnings, errors

    def as_markdown(self,) -> str:
        return f"""```
{self.asm}
```"""


class FV1FS(object):
    """
    A utility class representing the filesystem supported by the FV-1.

    The EEPROM image supported by the FV-1 is effectively 8 chunks of
    EEPROM of equal size (128 32-bit words each) containing the machine
    code for 8 different presets.
    """
    def __init__(self, adaptor=None) -> None:
        """
        Create an FV1 filesystem. If adaptor is None, this will operate in simulation mode.
        """
        self.adaptor = adaptor

#     def set_eeprom()

# def __get_eeprom(args, adaptor):
#     if args.sim:
#         from eeprom.eeprom import DummyEEPROM
#         return DummyEEPROM(args.sim, args.ee_size)

#     from eeprom.eeprom import I2CEEPROM
#     return I2CEEPROM(adaptor, args.ee_size, page_size_in_bytes=args.ee_page_size)
