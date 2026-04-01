"""
ModbusOEEClient — pymodbus 3.5+ synchronous TCP client service.
Reads machine data from HMI and writes OEE results back.
"""

import logging
import struct

_logger = logging.getLogger(__name__)

try:
    from pymodbus.client import ModbusTcpClient
    from pymodbus.exceptions import ModbusException
    PYMODBUS_AVAILABLE = True
except ImportError:
    PYMODBUS_AVAILABLE = False
    _logger.warning("pymodbus not installed. Run: pip install pymodbus>=3.5.0")


class ModbusOEEClient:
    """
    Synchronous Modbus TCP client wrapper for OEE data exchange.

    Usage:
        client = ModbusOEEClient(config_record)
        if client.connect():
            data = client.read_all_oee_inputs(register_map_records)
            client.write_all_oee_outputs(register_map_records, oee_results)
            client.disconnect()
    """

    def __init__(self, config_record):
        self.host = config_record.host
        self.port = config_record.port
        self.slave_id = config_record.slave_id
        self.timeout = config_record.timeout
        self.retries = config_record.retries
        self.reconnect_delay = config_record.reconnect_delay
        self._client = None

    # -------------------------------------------------------------------------
    # Connection
    # -------------------------------------------------------------------------

    def connect(self) -> bool:
        """Connect to Modbus TCP server. Returns True on success."""
        if not PYMODBUS_AVAILABLE:
            _logger.error("pymodbus not installed — cannot connect")
            return False
        try:
            self._client = ModbusTcpClient(
                host=self.host,
                port=self.port,
                timeout=self.timeout,
                retries=self.retries,
                reconnect_delay=self.reconnect_delay,
            )
            result = self._client.connect()
            if result:
                _logger.info("Modbus connected to %s:%s", self.host, self.port)
            else:
                _logger.warning("Modbus connection failed to %s:%s", self.host, self.port)
            return result
        except Exception as e:
            _logger.error("Modbus connect error: %s", e)
            return False

    def disconnect(self):
        """Close Modbus TCP connection."""
        try:
            if self._client:
                self._client.close()
                _logger.info("Modbus disconnected from %s:%s", self.host, self.port)
        except Exception as e:
            _logger.warning("Modbus disconnect error: %s", e)
        finally:
            self._client = None

    def is_connected(self) -> bool:
        return self._client is not None and self._client.is_active()

    # -------------------------------------------------------------------------
    # Read a single register
    # -------------------------------------------------------------------------

    def read_register(self, register_address: int, register_type: str,
                      data_type: str, scale_factor: float):
        """
        Read a single Modbus register.

        Returns:
            Scaled numeric value or bool, or None on error.
        """
        value, _ = self.read_register_with_detail(register_address, register_type, data_type, scale_factor)
        return value

    def read_register_with_detail(self, register_address: int, register_type: str,
                                  data_type: str, scale_factor: float):
        """
        Read a single Modbus register with detailed error reporting.

        Returns:
            Tuple (value, error_detail).
            On success: (scaled_value, None)
            On error: (None, "human readable error string")
        """
        if not self._client:
            msg = "Not connected — cannot read register %s" % register_address
            _logger.error(msg)
            return None, msg

        try:
            count = 2 if data_type == 'float32' else 1

            if register_type == 'holding':
                rr = self._client.read_holding_registers(register_address, count=count, device_id=self.slave_id)
            elif register_type == 'input':
                rr = self._client.read_input_registers(register_address, count=count, device_id=self.slave_id)
            elif register_type == 'coil':
                rr = self._client.read_coils(register_address, count=1, device_id=self.slave_id)
            elif register_type == 'discrete':
                rr = self._client.read_discrete_inputs(register_address, count=1, device_id=self.slave_id)
            else:
                msg = "Unknown register_type: %s" % register_type
                _logger.error(msg)
                return None, msg

            if rr is None:
                msg = "No response (timeout) from slave %s" % self.slave_id
                _logger.warning(msg)
                return None, msg

            if rr.isError():
                # Extract detailed Modbus error info
                error_class = type(rr).__name__
                msg = "Modbus error [%s]: %s (func=%s, addr=%s, device_id=%s)" % (
                    error_class, rr, register_type, register_address, self.slave_id)
                _logger.warning(msg)
                return None, msg

            # Parse value by data type
            if data_type == 'bool':
                value = bool(rr.bits[0]) if hasattr(rr, 'bits') else bool(rr.registers[0])
                return value, None

            if data_type == 'float32':
                # Combine two 16-bit registers into float32 (big-endian)
                raw = struct.pack('>HH', rr.registers[0], rr.registers[1])
                value = struct.unpack('>f', raw)[0]
            elif data_type == 'int16':
                raw = rr.registers[0]
                value = raw if raw < 32768 else raw - 65536
            else:  # uint16
                value = rr.registers[0]

            return value * scale_factor, None

        except ModbusException as e:
            msg = "ModbusException at addr %s: %s" % (register_address, e)
            _logger.error(msg)
            return None, msg
        except Exception as e:
            msg = "Unexpected error at addr %s: %s" % (register_address, e)
            _logger.error(msg)
            return None, msg

    # -------------------------------------------------------------------------
    # Write a single register
    # -------------------------------------------------------------------------

    def write_register(self, register_address: int, value,
                       data_type: str, scale_factor: float):
        """
        Write a value to a Modbus holding register.
        Applies inverse scale_factor before writing (raw = value / scale_factor).

        Args:
            register_address: 0-based register address
            value: numeric value to write (already in engineering units)
            data_type: 'uint16', 'int16', 'float32', 'bool'
            scale_factor: divisor to get raw integer
        """
        if not self._client:
            _logger.error("Not connected — cannot write register %s", register_address)
            return False

        try:
            if data_type == 'bool':
                rr = self._client.write_coil(register_address, bool(value), device_id=self.slave_id)
            elif data_type == 'float32':
                # Pack float into two 16-bit registers (big-endian)
                raw_bytes = struct.pack('>f', float(value))
                high, low = struct.unpack('>HH', raw_bytes)
                rr = self._client.write_registers(register_address, [high, low], device_id=self.slave_id)
            else:
                # uint16 / int16 — apply inverse scale
                if scale_factor and scale_factor != 0:
                    raw_val = int(round(float(value) / scale_factor))
                else:
                    raw_val = int(round(float(value)))
                # Clamp to uint16 range
                raw_val = max(0, min(65535, raw_val))
                rr = self._client.write_register(register_address, raw_val, device_id=self.slave_id)

            if rr is None or rr.isError():
                _logger.warning("Write error at address %s: %s", register_address, rr)
                return False

            _logger.debug("Written %s to register %s (raw after scale)", value, register_address)
            return True

        except ModbusException as e:
            _logger.error("ModbusException writing to address %s: %s", register_address, e)
            return False
        except Exception as e:
            _logger.error("Unexpected error writing to address %s: %s", register_address, e)
            return False

    # -------------------------------------------------------------------------
    # Batch read/write using register map
    # -------------------------------------------------------------------------

    def read_all_oee_inputs(self, register_map_records) -> dict:
        """
        Read all registers with direction 'read' or 'read_write'.

        Args:
            register_map_records: ORM recordset of mrp.modbus.register.map

        Returns:
            dict: {variable_key: value}
        """
        results = {}
        for reg in register_map_records:
            if reg.direction not in ('read', 'read_write'):
                continue
            value = self.read_register(
                reg.register_address,
                reg.register_type,
                reg.data_type,
                reg.scale_factor,
            )
            if value is not None:
                results[reg.variable_key] = value
                _logger.debug("Read %s = %s from register %s", reg.variable_key, value, reg.register_address)
        return results

    def write_all_oee_outputs(self, register_map_records, oee_results: dict):
        """
        Write OEE results to all registers with direction 'write' or 'read_write'.

        Args:
            register_map_records: ORM recordset of mrp.modbus.register.map
            oee_results: dict {variable_key: value}
        """
        for reg in register_map_records:
            if reg.direction not in ('write', 'read_write'):
                continue
            value = oee_results.get(reg.variable_key)
            if value is None:
                continue
            success = self.write_register(
                reg.register_address,
                value,
                reg.data_type,
                reg.scale_factor,
            )
            if success:
                _logger.info("Wrote OEE %s = %s to register %s", reg.variable_key, value, reg.register_address)
