# GPIOSim
Raspberry Pi GPIO simulator

http://bobvann.noip.me

**** What it does ****
That's actually a Raspberry Pi GPIO simulator for Linux/OS X (currently, Windows support coming soon)

With this simulator you can write and debug applications designed to be installed in the Raspberry Pi, 
interacting with the RPi.GPIO module for the GPIO header.


**** How does it work ****
The application has two parts:

GPIOSim.py  : the GUI
RPi/GPIO.py : the module

the module is designed to replace the real RPi.GPIO module in a GPIO-less machine (e.g. your PC).

Once you correctly install it your application will see no difference between the real GPIO module and mine.

Instead of writing to the GPIO header, it writes to a file saved in /tmp (will be c:\Temp on Windows).

The GUI just reads from the file and displays the info like a GPIO header.
Output set pins are read-only, while it is possible to toggle the state of input pins just clicking on them.

It also offer the possibility to simulate the reboot of the RPi, which sets pins back to default.
Please note that rebooting the real PC will result in a simulated RPi reboot.

The GUI updates only when it gets a process signal from the module (here's why it doesn't support Win yet).


***** Notes *****

At the moment the simulated module provides only the following methods:


- GPIO.setup(pin, mode, pull_up_down=PUD_OFF)

- GPIO.output(pin, value)

- GPIO.input(pin)

- GPIO.set_high(pin)

- GPIO.set_low(pin)

- GPIO.is_high(pin)

- GPIO.is_low(pin)

- GPIO.output_pins(pins)

- GPIO.setup_pins(pins)

- GPIO.input_pins(pins)

I have not implemented the remaining methods (interrupts, event callbacks, etc) but I will soon.



**** Installation ****

- copy the RPi folder inside your python3.x modules folder (e.g. /usr/lib/python3.x/ )

- copy the GPIOSim.py file where you like, chmod +x it and run it :)