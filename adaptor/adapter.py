from abc import ABC, abstractmethod

import sys
import time


class Adaptor(ABC):
    def __init__(self, ):
        pass

    @abstractmethod
    def open(self,):
        """Opens a connection to a device."""
        pass

    @abstractmethod
    def close(self,):
        """Closes the connection to a device."""
        pass

    @abstractmethod
    def read_bytes(self, num_bytes):
        """Reads a series of bytes from a device."""
        pass

    @abstractmethod
    def write_bytes(self, byte_list):
        """
        Writes a list of bytes to a device.
        """
        pass

    @abstractmethod
    def write_then_read_bytes(self, byte_list, num_read_bytes):
        """
        Writes a list of bytes to a device, then reads num_read_bytes.
        """
        pass


class I2CAdaptor(Adaptor):
    def __init__(self, i2c_address, i2c_clock_speed):
        super(I2CAdaptor, self).__init__()
        self.i2c_address = i2c_address
        self.i2c_clock_speed = i2c_clock_speed

    @property
    def address(self,):
        return self.i2c_address

    @property
    def speed(self,):
        return self.i2c_clock_speed
