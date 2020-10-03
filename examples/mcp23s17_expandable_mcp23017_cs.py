# SPDX-FileCopyrightText: 2020 Romy Bompart
#
# SPDX-License-Identifier: MIT

# Demo of using six (6) MCP23S17 as I/O expander and one (1) MCP23017 as chip select 
# The MCP23S17 will be used for reading digital inputs, but it can be used for output 
# by using the switch_to_output function instead of direction = Digitalio.INPUT
# for the MCP23S17's 
# Author: Romy Bompart 

import time
import busio
import board
from digitalio import Direction, Pull, DigitalInOut
from adafruit_mcp23sxx.mcp23s17 import MCP23S17
from adafruit_mcp230xx.mcp23017 import MCP23017

#Class to create a MCP23S17 device 
class MCP23S17_module():

	#cs_pin_num represent the GPIO number from the MCP23017 that will be used 
	#to activate the cs during the communication

	cs_pin_num = [8,9,10,11,12,13]

	#constructor to assign the SPI and what chip select is going to be activated
	#for the particular MCP23S17
	def __init__(self, cs_pin = None, address = 0x20):
		self.cs_enable = cs_pin
		self.spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
		self.mcp_spi = MCP23S17(self.spi, self.cs_enable, address)
		self.pin = []
		self.mcp = []

#creating a MCP23017 to use it as chip select for the MCP23S17
i2c = busio.I2C(board.SCL, board.SDA)
chip_ic = MCP23017(i2c,0x27)
pin = []

#Becuase I am not using pull ups resistors for the chip select, first, initialize 
# the cs as high logic voltage. 
print ( "INIT PULL UPS SPI ")
for pin_num in range(16):
	pin.append(chip_ic.get_pin(pin_num))
	pin[pin_num].direction = Direction.OUTPUT
	pin[pin_num].pull = Pull.UP
	pin[pin_num].value = True
	print("pin {} configured... ".format(pin_num))
	time.sleep(0.2)

#create the MCP23S17 devices. 
print ( "*" * 50 )
mcp = []
for mcp_num in range (6):
	# The HAEN bit is enabled by default when the MCP23S17 is created, thus the address
	# will be taken from the external pins A0,A1 and A2. 
	# in this example the address are 0x20,0x21...0x25
	address = 0x20 + mcp_num
	#create a list of MCP23S17, and provide the chip select pin from the chip_ic instance
	#which is the comming from the MCP23017. !!!! This is awensome I believe.
	#the MCP23017 I/O can be accessible from the Adafruit SPI library by doing this.
	mcp.append(MCP23S17_module(chip_ic.get_pin(MCP23S17_module.cs_pin_num[mcp_num]),address))
	print ( "MCP23S17 #{} , cs = {}".format(mcp_num,MCP23S17_module.cs_pin_num[mcp_num]))
	#reading the ICON register to make sure the register is well configured it shall be 0x08
	#for more information read the datasheet 
	print ( "MCP iocontrol register 0x{:02x} = 0x{:02x}".format(0x0A,mcp[mcp_num].mcp_spi.io_control))
	# create the pins object for the MCP23S17
	for pin_num in range(16):
		print ( "configuring pin [{}]".format(pin_num))
		mcp[mcp_num].pin.append(mcp[mcp_num].mcp_spi.get_pin(pin_num))
		mcp[mcp_num].pin[pin_num].direction = Direction.INPUT
		mcp[mcp_num].pin[pin_num].pull = Pull.UP

i = 0
while (i<5):

	for mcp_num in range(6):
		address = 0x20 + mcp_num
		print ( "*" * 50 )
		print("MCP23S17, address = 0x{:02x}, cs = {}".format(address,MCP23S17_module.cs_pin_num[mcp_num]))

		#read all the digital inputs for the MCP23S17
		for pin_num in range(16):
			print("GPIO[{}] = {}".format(pin_num,mcp[mcp_num].pin[pin_num].value))	
			time.sleep(0.1)
			input()
		
		time.sleep(0.2)
	
	i = i + 1

print ("test finished")
exit()
