#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#
# GPIOSim
#
# Bob Vann - http://bobvann.noip.me
#
# https://github.com/bobvann/GPIOSim
# 
# Requires Python 3

import os, tempfile,signal
from configparser import RawConfigParser

OUT     = 2
IN      = 1
HIGH    = 1
LOW     = 0

RISING      = 1
FALLING     = 2
BOTH        = 3

PUD_OFF  = 0
PUD_DOWN = 1
PUD_UP   = 2


WORK_DIR = os.path.join(tempfile.gettempdir(), "GPIOSim")
WORK_FILE = os.path.join(WORK_DIR, "pins.ini")

GPIO_NAMES = [
    "3v3","5v",
    "GPIO2","5V",
    "GPIO3","GND",
    "GPIO4","GPIO14",
    "GND","GPIO15",
    "GPIO17","GPIO18",
    "GPIO27","GND",
    "GPIO22","GPIO23",
    "3V3","GPIO24",
    "GPIO10","GND",
    "GPIO9","GPIO25",
    "GPIO11","GPIO8",
    "GND","GPIO7",
    "I2C","I2C",
    "GPIO5","GND",
    "GPIO6","GPIO12",
    "GPIO13","GND",
    "GPIO19","GPIO16",
    "GPIO26","GPIO20",
    "GND","GPIO21"
]

def check():
	if not os.path.exists(WORK_FILE):
		print("")
		print("You have not started GPIOSIm since")
		print("you last restarted your computer.")
		print("")
		print("Please start the GPIOSim GUI and ")
		print("then try again.")
		print("")
		print("")

		raise Exception

    

def setup(pin, mode, pull_up_down=PUD_OFF):
    """Set the input or output mode for a specified pin.  Mode should be
    either OUT or IN."""
    check()
        
    c = RawConfigParser()
    c.read(WORK_FILE)

    pin = GPIO_NAMES.index("GPIO"+str(pin))

    if c.getint("pin"+str(pin),"state") == 0:
        raise Exception

    c.set("pin"+str(pin),"state",str(mode))
    if mode==OUT:
        c.set("pin"+str(mode),"value","0")
    with open(WORK_FILE, 'w') as configfile:
            c.write(configfile)

    pid = os.popen("ps ax | grep GPIOSim | head -1 | awk '{print $1}'").read()
    os.kill(int(pid), signal.SIGUSR1)

def output(pin, value):
    """Set the specified pin the provided high/low value.  Value should be
    either HIGH/LOW or a boolean (true = high)."""
    check()
    
    c = RawConfigParser()
    c.read(WORK_FILE)

    pin = GPIO_NAMES.index("GPIO"+str(pin))

    if c.getint("pin"+str(pin),"state") != OUT:
        raise Exception

    c.set("pin"+str(pin),"value",str(value))

    with open(WORK_FILE, 'w') as configfile:
            c.write(configfile)

    pid = os.popen("ps ax | grep GPIOSim | head -1 | awk '{print $1}'").read()
    os.kill(int(pid), signal.SIGUSR1)

def input(pin):
    """Read the specified pin and return HIGH/true if the pin is pulled high,
    or LOW/false if pulled low."""
    check()

    pin = GPIO_NAMES.index("GPIO"+str(pin))
    
    c = RawConfigParser()
    c.read(WORK_FILE)

    return c.getint("pin"+str(pin),"value")


def set_high(pin):
    """Set the specified pin HIGH."""
    check()
    output(pin, HIGH)


def set_low(pin):
    """Set the specified pin LOW."""
    check()
    output(pin, LOW)

def is_high(pin):
    """Return true if the specified pin is pulled high."""
    check()
    return input(pin) == HIGH

def is_low(pin):
    """Return true if the specified pin is pulled low."""
    check()
    return input(pin) == LOW


# Basic implementation of multiple pin methods just loops through pins and
# processes each one individually. This is not optimal, but derived classes can
# provide a more optimal implementation that deals with groups of pins
# simultaneously.
# See MCP230xx or PCF8574 classes for examples of optimized implementations.

def output_pins(pins):
    check()

    for pin, value in iter(pins.items()):
        output(pin, value)

def setup_pins(pins):
    check()
    for pin, value in iter(pins.items()):
        setup(pin, value)

def input_pins(pins):
    check()
    return [input(pin) for pin in pins]


def add_event_detect(pin, edge):
    """Enable edge detection events for a particular GPIO channel.  Pin 
    should be type IN.  Edge must be RISING, FALLING or BOTH.
    """
    check()
    raise NotImplementedError

def remove_event_detect(pin):
    """Remove edge detection for a particular GPIO channel.  Pin should be
    type IN.
    """
    check()
    raise NotImplementedError

def add_event_callback(pin, callback):
    """Add a callback for an event already defined using add_event_detect().
    Pin should be type IN.
    """
    check()
    raise NotImplementedError

def event_detected(pin):
    """Returns True if an edge has occured on a given GPIO.  You need to 
    enable edge detection using add_event_detect() first.   Pin should be 
    type IN.
    """
    check()
    raise NotImplementedError

def wait_for_edge(pin, edge):
    """Wait for an edge.   Pin should be type IN.  Edge must be RISING, 
    FALLING or BOTH."""
    check()
    raise NotImplementedError

def cleanup(pin=None):
    """Clean up GPIO event detection for specific pin, or all pins if none 
    is specified.
    """
    check()
    raise NotImplementedError


# helper functions useful to derived classes

def _validate_pin(pin):
    # Raise an exception if pin is outside the range of allowed values.
    check()
    if (pin not in PINS_A) and (pin not in PINS_B):
        raise ValueError('Invalid GPIO value, must be between A0 AND A7 or between B0 AND B7')

# no idea what is this and if I should iplement it
#def _bit2( src, bit, val):
    #bit = 1 << bit
    #return (src | bit) if val else (src & ~bit)

