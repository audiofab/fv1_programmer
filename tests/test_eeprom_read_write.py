import pytest
import secrets
import pathlib

from adaptor.mcp2221 import MCP2221I2CAdaptor
from eeprom.eeprom import I2CEEPROM


@pytest.fixture
def adaptor():
    adaptor = MCP2221I2CAdaptor(0x50, i2c_clock_speed=400000)
    adaptor.open()
    yield adaptor

@pytest.fixture
def i2c_ee(adaptor):
    yield I2CEEPROM(adaptor, size_in_bytes=4096, page_size_in_bytes=32)


def test_erase_EEPROM(i2c_ee):
    all_zeroes = bytes([0x0]*i2c_ee.size)
    all_ones = bytes([0xff]*i2c_ee.size)
    checkerboard1 = bytes([0xA5]*i2c_ee.size)
    checkerboard2 = bytes([0xA5]*i2c_ee.size)

    # Fill with ones
    i2c_ee.write_bytes(0, all_ones)
    _read = i2c_ee.read_bytes(0, i2c_ee.size)
    assert _read == all_ones

    # Fill with zeroes
    i2c_ee.write_bytes(0, all_zeroes)
    _read = i2c_ee.read_bytes(0, i2c_ee.size)
    assert _read == all_zeroes

    # Fill with ones
    i2c_ee.write_bytes(0, all_ones)
    _read = i2c_ee.read_bytes(0, i2c_ee.size)
    assert _read == all_ones


def test_checkerboard(i2c_ee):
    checkerboard1 = bytes([0xA5]*i2c_ee.size)
    checkerboard2 = bytes([0xA5]*i2c_ee.size)

    i2c_ee.write_bytes(0, checkerboard1)
    _read = i2c_ee.read_bytes(0, i2c_ee.size)
    assert _read == checkerboard1

    i2c_ee.write_bytes(0, checkerboard2)
    _read = i2c_ee.read_bytes(0, i2c_ee.size)
    assert _read == checkerboard2


def test_partial_write(i2c_ee):
    empty = bytes([0xff]*i2c_ee.size)

    # Erase EEPROM
    i2c_ee.write_bytes(0, empty)
    _read = i2c_ee.read_bytes(0, i2c_ee.size)
    assert _read == empty

    _rand = secrets.token_bytes(4096)
    assert _read != _rand

    i2c_ee.write_bytes(0, _rand)
    _read = i2c_ee.read_bytes(0, i2c_ee.size)
    assert _read == _rand

    # Erase EEPROM
    i2c_ee.write_bytes(0, empty)
    _read = i2c_ee.read_bytes(0, i2c_ee.size)
    assert _read == empty

    # Overwrite partial pages
    i2c_ee.write_bytes(3, _rand[3:577])
    _read = i2c_ee.read_bytes(0, i2c_ee.size)
    assert _read != _rand
    assert _read[0:3] != _rand[0:3]
    assert _read[3:577] == _rand[3:577]
    assert _read[577:] != _rand[577:]

    # Re-write entire EEPROM
    i2c_ee.write_bytes(0, _rand)
    _read = i2c_ee.read_bytes(0, i2c_ee.size)
    assert _read == _rand


def test_load_bin(i2c_ee):
    this_path = pathlib.Path(__file__).parent.resolve()
    i2c_ee.load_bin(this_path / 'backup.bin', verify=True)

def test_load_hex(i2c_ee):
    this_path = pathlib.Path(__file__).parent.resolve()
    i2c_ee.load_hex(this_path / 'reverbs.hex', verify=True)
