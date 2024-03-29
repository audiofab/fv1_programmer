import pytest
import secrets
import pathlib

from adaptor.mcp2221 import MCP2221I2CAdaptor
from eeprom.eeprom import EEPROM, I2CEEPROM


@pytest.fixture
def adaptor():
    adaptor = MCP2221I2CAdaptor(0x50, i2c_clock_speed=400000)
    adaptor.open()
    yield adaptor

@pytest.fixture
def i2c_ee(adaptor):
    yield I2CEEPROM(adaptor, size_in_bytes=4096, page_size_in_bytes=32)


def test_split_transaction():
    transactions = EEPROM.split_transaction(32, 0, 4096)
    expected = []
    for addr in range(0, 4096, 32):
        expected.append((addr, addr, 32))
    assert transactions == expected

    transactions = EEPROM.split_transaction(65535, 0, 4096)
    expected = [(0, 0, 4096)]
    assert transactions == expected

    transactions = EEPROM.split_transaction(65535, 0, 512)
    expected = [(0, 0, 512)]
    assert transactions == expected


def test_erase_EEPROM(i2c_ee):
    # Fill with ones
    i2c_ee.erase(0xFF, verify=True)

    # Fill with zeroes
    i2c_ee.erase(0, verify=True)

    # Fill with ones
    i2c_ee.erase(0xFF, verify=True)


def test_checkerboard(i2c_ee):
    i2c_ee.erase(0xA5, verify=True)
    i2c_ee.erase(0x5A, verify=True)


def test_partial_write(i2c_ee):
    # Erase EEPROM
    i2c_ee.erase(0xFF, verify=True)

    _read = i2c_ee.read_bytes(0, i2c_ee.size)

    _rand = secrets.token_bytes(4096)
    assert _read != _rand

    i2c_ee.write_bytes(0, _rand)
    _read = i2c_ee.read_bytes(0, i2c_ee.size)
    assert _read == _rand

    # Erase EEPROM
    i2c_ee.erase(0xFF, verify=True)

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


def test_write_and_verify_in_chunks(i2c_ee):
    # Erase EEPROM
    i2c_ee.erase(0xFF, verify=True)

    _read = i2c_ee.read_bytes(0, i2c_ee.size)

    _rand = secrets.token_bytes(4096)
    assert _read != _rand

    for addr in range(0, i2c_ee.size, 512):
        i2c_ee.write_bytes(addr, _rand[addr:addr+512])

    for addr in range(0, i2c_ee.size, 512):
        _read = i2c_ee.read_bytes(addr, 512)
        assert _read == _rand[addr:addr+512]


def test_write_in_chunks_and_verify_in_one_shot(i2c_ee):
    # Erase EEPROM
    i2c_ee.erase(0xFF, verify=True)

    _read = i2c_ee.read_bytes(0, i2c_ee.size)

    _rand = secrets.token_bytes(4096)
    assert _read != _rand

    for addr in range(0, i2c_ee.size, 512):
        i2c_ee.write_bytes(addr, _rand[addr:addr+512])

    _read = i2c_ee.read_bytes(0, i2c_ee.size)

    for addr in range(0, i2c_ee.size, 512):
        assert _read[addr:addr+512] == _rand[addr:addr+512]


def test_load_bin(i2c_ee):
    this_path = pathlib.Path(__file__).parent.resolve()
    i2c_ee.load_file(this_path / 'backup.bin', verify=True)

def test_load_hex(i2c_ee):
    this_path = pathlib.Path(__file__).parent.resolve()
    i2c_ee.load_file(this_path / 'reverbs.hex', verify=True)

def test_load_file_fail(i2c_ee):
    this_path = pathlib.Path(__file__).parent.resolve()
    with pytest.raises(ValueError) as exc_info:
        i2c_ee.load_file(this_path / 'dummy.txt', verify=True)
