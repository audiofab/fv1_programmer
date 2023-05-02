from abc import ABC, abstractmethod
from adaptor.adapter import Adaptor

import logging
from pathlib import Path
from intelhex import IntelHex


_MAX_TRANSACTION_SIZE = 65535
_DEFAULT_PAGE_SIZE = 32

logger = logging.getLogger('eeprom')


class EEPROM(ABC):
    def __init__(self, adaptor : Adaptor, size_in_bytes : int, page_size_in_bytes : int =_DEFAULT_PAGE_SIZE) -> None:
        assert size_in_bytes > 0, "Size must be > 0"
        assert size_in_bytes % page_size_in_bytes == 0, "Size must be a multiple of page size"
        self.size_in_bytes = size_in_bytes
        self.page_size_in_bytes = page_size_in_bytes
        self.adaptor = adaptor

    @property
    def size(self,):
        return self.size_in_bytes

    @property
    def page_size(self,):
        return self.page_size_in_bytes

    @abstractmethod
    def read_bytes(self, byte_address, num_bytes):
        """Reads a series of sequential bytes from EEPROM."""
        pass

    @abstractmethod
    def write_bytes(self, byte_address, byte_list):
        """
        Writes a list of bytes to EEPROM.
        """
        pass

    @staticmethod
    def ensure_bytes(data):
        if type(data) == bytes:
            return data
        elif type(data) == int:
            return bytes([data])
        elif type(data) == list:
            return bytes(data)
        raise ValueError("Invalid data format. Acceptable values are int, list or bytes.")

    @staticmethod
    def split_transaction(max_size, start_address, total_bytes):
        """
        Splits a large transaction into max_size-aligned transactions.
        Returns a list of tuples of (address, offset, length) for each transaction.
        """
        aligned_size = (max_size - start_address) % max_size
        first_length = aligned_size if aligned_size != 0 else min(max_size, total_bytes)
        transactions = [(start_address, 0, first_length),]
        current_address = start_address + first_length
        current_offset = 0 + first_length

        bytes_left = total_bytes - first_length

        while bytes_left > 0:
            if bytes_left < max_size:
                # This is the last/partial transaction
                transactions.append((current_address, current_offset, bytes_left))
            else:
                # Another full page
                transactions.append((current_address, current_offset, max_size))
            current_address += max_size
            current_offset += max_size
            bytes_left -= max_size

        return transactions

    def load_file(self, filepath : Path, padding=0xFF, verify : bool=False):
        """
        Loads a file onto the connected EEPROM.
        """
        assert filepath.is_file() and filepath.exists(), f"Invalid file path {str(filepath)}"
        if filepath.suffix.lower() == '.hex':
            return self.load_hex(filepath, padding=padding, verify=verify)
        elif filepath.suffix.lower() == '.bin':
            return self.load_bin(filepath, verify=verify)

        raise ValueError(f"Don't know how to handle file suffix '{filepath.suffix}'")

    def load_hex(self, filepath : Path, padding=0xFF, verify : bool=False):
        """
        Loads a hex file onto the connected EEPROM.
        """
        hex_file = IntelHex(str(filepath))
        hex_file.padding = padding
        write_data = hex_file.tobinstr(start=0, size=self.size)
        self.write_bytes(0, write_data)
        if verify:
            readback = self.read_bytes(0, self.size)
            assert readback == write_data

    def load_bin(self, filepath : Path, verify : bool=False):
        """
        Loads a binary file onto the connected EEPROM.
        """
        with open(filepath, 'rb') as f:
            write_data = f.read(self.size)
            assert len(write_data) <= self.size
            self.write_bytes(0, write_data)
            if verify:
                readback = self.read_bytes(0, self.size)
                assert readback == write_data

    def save_file(self, filepath : Path):
        """
        Dumps the entire contents of EEPROM to a binary file.
        """
        with open(filepath, 'wb') as f:
            f.write(self.read_bytes(0, self.size))

    def erase(self, byte_value : int, verify : bool=False):
        """
        Erase the EEPROM by filling it with `byte_value`
        """
        erase_bytes = bytes([byte_value]*self.size)
        self.write_bytes(0, erase_bytes)
        if verify:
            assert self.read_bytes(0, self.size) == erase_bytes


class I2CEEPROM(EEPROM):
    def read_bytes(self, byte_address, num_bytes):
        _bytes = b''
        for _addr, _offset, _len in EEPROM.split_transaction(_MAX_TRANSACTION_SIZE, byte_address, num_bytes):
            # logger.debug(_addr, _offset, _len)
            # Send the 16-bit byte address followed by the read
            _bytes += self.adaptor.write_then_read_bytes(_addr.to_bytes(2, 'big'), _len)

        return _bytes

    def write_bytes(self, byte_address, byte_list):
        # Perform the write, split on page boundaries
        for _addr, _offset, _len in EEPROM.split_transaction(self.page_size, byte_address, len(byte_list)):
            # logger.debug(_addr, _offset, _len)
            self.adaptor.write_bytes(_addr.to_bytes(2, 'big') + EEPROM.ensure_bytes(byte_list[_offset:_offset+_len]))

