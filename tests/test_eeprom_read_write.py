import pytest
import secrets

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


def test_erase_and_readback(i2c_ee):
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
