#!/usr/bin/env python

# Based on Morningstar documentation here
# http://www.morningstarcorp.com/wp-content/uploads/2014/02/TSMPPT.APP_.Modbus.EN_.10.2.pdf
# and heavily modified version of the script here
# http://www.fieldlines.com/index.php?topic=147639.0

import time
counter = 0

import sys

if len(sys.argv) <= 1:
    print "Usage: read_registers.py <ip address 1> [ip address 2] ..."
    exit(1)

hosts = sys.argv[1:]

# import the server implementation
from pymodbus.client.sync import ModbusTcpClient as ModbusClient

# configure the client logging
import logging
logging.basicConfig()
log = logging.getLogger('./modbus.error')
log.setLevel(logging.ERROR)

for host in hosts:
 print "Host %s" % host
 client = ModbusClient(host,502)
 client.connect()

# Define the State list
 state = ['Start', 'Night Check', 'Disconnected', 'Night', 'Fault!', 'MPPT', 'Absorption', 'FloatCharge', 'Equalizing', 'Slave']

# read registers. Start at 0 for convenience
 rr = client.read_holding_registers(0,80,1)

# for all indexes, subtract 1 from what's in the manual
 V_PU_hi = rr.registers[0]
 V_PU_lo = rr.registers[1]
 I_PU_hi = rr.registers[2]
 I_PU_lo = rr.registers[3]

 V_PU = float(V_PU_hi) + float(V_PU_lo)
 I_PU = float(I_PU_hi) + float(I_PU_lo)

 v_scale = V_PU * 2**(-15)
 i_scale = I_PU * 2**(-15)
 p_scale = V_PU * I_PU * 2**(-17)

# battery sense voltage, filtered
 battsV = rr.registers[24] * v_scale
 battsSensedV = rr.registers[26] * v_scale
 battsI = rr.registers[28] * i_scale
 arrayV = rr.registers[27] * v_scale
 arrayI = rr.registers[29] * i_scale
 statenum = rr.registers[50]
 hsTemp = rr.registers[35] 
 rtsTemp = rr.registers[36]
 outPower = rr.registers[58] * p_scale
 inPower = rr.registers[59] * p_scale
 minVb_daily = rr.registers[64] * v_scale
 maxVb_daily = rr.registers[65] * v_scale
 minTb_daily = rr.registers[71]
 maxTb_daily = rr.registers[72]
 dipswitches = bin(rr.registers[48])[::-1][:-2].zfill(8)
 led_state = rr.registers
 print "battery voltage: %.2f" % battsV
 print "battery sensing: %.2f" % battsSensedV
 print "battery current: %.2f" % battsI
 print "battery watts:   %.2f" % (battsV*battsI)
 print "array voltage:   %.2f" % arrayV
 print "array current:   %.2f" % arrayI
 print "array watts:     %.2f" % (arrayV*arrayI)
 print "heat sink temp:  %.2f" % hsTemp
 print "battery temp:    %.2f" % rtsTemp
 print "state:           %s" % state[statenum]
 print "out power:       %0.2f" % outPower
 print "in Power:        %0.2f" % inPower
 print "min Vb daily:    %0.2f" % minVb_daily
 print "max Vb daily:    %0.2f" % maxVb_daily
 print "min Tb daily:    %0.2f" % minTb_daily
 print "max Tb daily:    %0.2f" % maxTb_daily
 print "dipswitches:     %s" % dipswitches
 print "dipswitches:     12345678"
 print ""
 client.close()
