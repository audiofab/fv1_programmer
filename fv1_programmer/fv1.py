from asfv1.asfv1 import fv1parse, ASFV1Error
from disfv1.disfv1 import fv1deparse
from typing import Tuple


FV1_PROGRAM_MAX_BYTES = 512

class FV1Program(object):
    def __init__(self, asm) -> None:
        self.asm = asm

    def assemble(self, clamp=True, spinreals=False) -> Tuple[bytearray, str, str]:
        """
        Assembles our internal asm to a bytearray, returning any errors and warnings
        as concatenated strings.
        """
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
            return None, fp.icnt, warnings, errors

        return fp.program, fp.icnt, warnings, errors

    def from_bytearray(self, data : bytearray, relative=False, suppressraw=False) -> str:
        """
        Disassembles a binary FV1 program and sets the internal asm property to
        the disassembled output. Returns any warnings in a concatenated string.
        """
        warnings = []

        def warning(msg):
            nonlocal warnings
            warnings.append(msg)

        fp = fv1deparse(data,
                        relative=relative, nopraw=suppressraw,
                        wfunc=warning)
        fp.deparse()
        self.asm = fp.listing

        return warnings

    @property
    def assembly(self,) -> str:
        return self.asm
