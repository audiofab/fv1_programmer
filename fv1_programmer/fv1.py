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

    def as_markdown(self,) -> str:
        return f"""```{self.asm}```"""


class FV1FS(object):
    """
    A utility class representing the filesystem supported by the FV-1.

    The EEPROM image supported by the FV-1 is effectively 8 chunks of
    EEPROM of equal size (128 32-bit words each) containing the machine
    code for 8 different presets.
    """
    def __init__(self) -> None:
        pass
