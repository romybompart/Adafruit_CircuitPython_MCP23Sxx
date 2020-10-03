# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2019 Carter Nelson
#
# SPDX-License-Identifier: MIT

"""
`digital_inout`
====================================================

Digital input/output of the MCP23Sxx.

* Author(s): Tony DiCola
* Contributor(s): Romy Bompart (2020)
"""

import digitalio

__version__ = ""
__repo__ = ""

# Internal helpers to simplify setting and getting a bit inside an integer.
def _get_bit(val, bit):
    return val & (1 << bit) > 0


def _enable_bit(val, bit):
    return val | (1 << bit)


def _clear_bit(val, bit):
    return val & ~(1 << bit)


class DigitalInOut:
    """Digital input/output of the MCP23Sxx.  The interface is exactly the
    same as the digitalio.DigitalInOut class, however:

      * MCP23Sxx family does not support pull-down resistors;

    Exceptions will be thrown when attempting to set unsupported pull
    configurations.
    """

    def __init__(self, pin_number, mcp23sxx):
        """Specify the pin number of the MCP23S17, 0...15 instance.
        """
        self._pin = pin_number
        self._mcp = mcp23sxx

    # kwargs in switch functions below are _necessary_ for compatibility
    # with DigitalInout class (which allows specifying pull, etc. which
    # is unused by this class).  Do not remove them, instead turn off pylint
    # in this case.
    # pylint: disable=unused-argument
    def switch_to_output(self, value=False, **kwargs):
        """Switch the pin state to a digital output with the provided starting
        value (True/False for high or low, default is False/low).
        """
        self.direction = digitalio.Direction.OUTPUT
        self.value = value

    def switch_to_input(self, pull=None, **kwargs):
        """Switch the pin state to a digital input with the provided starting
        pull-up resistor state (optional, no pull-up by default).  Note that
        pull-down resistors are NOT supported!
        """
        self.direction = digitalio.Direction.INPUT
        self.pull = pull

    # pylint: enable=unused-argument

    @property
    def value(self):
        """The value of the pin, either True for high or False for
        low.  Note you must configure as an output or input appropriately
        before reading and writing this value.
        """
        return _get_bit(self._mcp.gpio, self._pin)

    @value.setter
    def value(self, val):
        if val:
            self._mcp.gpio = _enable_bit(self._mcp.gpio, self._pin)
        else:
            self._mcp.gpio = _clear_bit(self._mcp.gpio, self._pin)

    @property
    def direction(self):
        """The direction of the pin, either True for an input or
        False for an output.
        """
        if _get_bit(self._mcp.iodir, self._pin):
            return digitalio.Direction.INPUT
        return digitalio.Direction.OUTPUT

    @direction.setter
    def direction(self, val):
        if val == digitalio.Direction.INPUT:
            self._mcp.iodir = _enable_bit(self._mcp.iodir, self._pin)
        elif val == digitalio.Direction.OUTPUT:
            self._mcp.iodir = _clear_bit(self._mcp.iodir, self._pin)
        else:
            raise ValueError("Expected INPUT or OUTPUT direction!")

    @property
    def pull(self):
        """Enable or disable internal pull-up resistors for this pin.  A
        value of digitalio.Pull.UP will enable a pull-up resistor, and None will
        disable it.  Pull-down resistors are NOT supported!
        """
        try:
            if _get_bit(self._mcp.gppu, self._pin):
                return digitalio.Pull.UP
        except AttributeError as error:
            # MCP23016 doesn't have a `gppu` register.
            raise ValueError("Pull-up/pull-down resistors not supported.") from error
        return None

    @pull.setter
    def pull(self, val):
        try:
            if val is None:
                self._mcp.gppu = _clear_bit(self._mcp.gppu, self._pin)
            elif val == digitalio.Pull.UP:
                self._mcp.gppu = _enable_bit(self._mcp.gppu, self._pin)
            elif val == digitalio.Pull.DOWN:
                raise ValueError("Pull-down resistors are not supported!")
            else:
                raise ValueError("Expected UP, DOWN, or None for pull state!")
        except AttributeError as error:
            # MCP23016 doesn't have a `gppu` register.
            raise ValueError("Pull-up/pull-down resistors not supported.") from error
