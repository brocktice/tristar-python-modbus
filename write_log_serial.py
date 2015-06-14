#!/usr/bin/env python

# Based on Morningstar documentation here
# http://www.morningstarcorp.com/wp-content/uploads/2014/02/TSMPPT.APP_.Modbus.EN_.10.2.pdf
# and heavily modified version of the script here
# http://www.fieldlines.com/index.php?topic=147639.0

# This is modified for the non-MPPT tri-stars without built-in network monitoring. It has different indices and different available data.

import sys
import re
import time

# import the server implementation
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

# configure the client logging
import logging
logging.basicConfig()
log = logging.getLogger('./modbus.error')
log.setLevel(logging.ERROR)

client = ModbusClient(method='rtu',port='/dev/ttyUSB0', baudrate=9600, timeout=1)
client.connect()
log.debug(client)

# Define the State list
state = ['Start', 'Night Check', 'Disconnected', 'Night', 'Fault!', 'BulkCharge', 'Absorption', 'FloatCharge', 'Equalizing']

# read registers. Start at 0 for convenience
rr = client.read_holding_registers(0,37,1)
if rr == None:
    client.close()
    log.error("couldn't connect")
    exit(1)

# for all indexes, subtract 1 from what's in the manual
v_scale = 96.667 * 2**(-15)
i_scale = 66.667 * 2**(-15)
array_scale = 139.15 * 2**(-15)

# battery terminal voltage
battsV = rr.registers[8] * v_scale

# load current
# battsI = rr.registers[12] * i_scale * 4.75

# array voltage
arrayV = rr.registers[10] * array_scale

# charge current
arrayI = rr.registers[11] * i_scale

# charge state
statenum = rr.registers[27]

# heat sink temperature
hsTemp = rr.registers[14] 

# configuration dipswitches
dipswitches = bin(rr.registers[25])[::-1][:-2].zfill(8)

print "%s B: %.2fV\tP: %.2fV\tC: %.2fA\tPow: %.2fW\tS: %s" % (time.strftime("%Y-%m-%dT%H:%M:%S%Z"), battsV, arrayV, arrayI, battsV*arrayI, state[statenum]) 
client.close()
