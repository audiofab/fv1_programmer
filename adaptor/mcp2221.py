import EasyMCP2221
from .adapter import I2CAdaptor


class MCP2221I2CAdaptor(I2CAdaptor):
    def __init__(self, i2c_address, i2c_clock_speed=100000, transaction_timeout_ms=20):
        super(MCP2221I2CAdaptor, self).__init__(i2c_address, i2c_clock_speed)
        self.timeout = transaction_timeout_ms
        self.mcp = None

    def open(self,):
        self.mcp = EasyMCP2221.Device()
        self.mcp.I2C_speed(self.speed)

        # Ensure there is something connected by doing a dummy read
        return self.mcp.I2C_read(self.address)

    def close(self,):
        pass

    def read_bytes(self, num_bytes):
        return self.mcp.I2C_read(self.address, size=num_bytes, timeout_ms=self.timeout)

    def write_bytes(self, byte_list):
        self.mcp.I2C_write(self.address, byte_list, timeout_ms=self.timeout)

    def write_then_read_bytes(self, byte_list, num_read_bytes):
        self.mcp.I2C_write(self.address, byte_list, kind='nonstop', timeout_ms=self.timeout)
        return self.mcp.I2C_read(self.address, num_read_bytes, kind='restart', timeout_ms=self.timeout)
