# IR Receiver

##### [Main README](./README.md#1-ir-communication)

# 1. Hardware Requirements

The receiver is cross-platform. It requires an IR receiver chip to demodulate
the carrier. The chip must be selected for the frequency in use by the remote.
For 38KHz devices a receiver chip such as the Vishay TSOP4838 or the
[adafruit one](https://www.adafruit.com/products/157) is required. This
demodulates the 38KHz IR pulses and passes the demodulated pulse train to the
microcontroller. The tested chip returns a 0 level on carrier detect, but the
driver design ensures operation regardless of sense.

In my testing a 38KHz demodulator worked with 36KHz and 40KHz remotes, but this
is obviously neither guaranteed nor optimal.

The pin used to connect the decoder chip to the target is arbitrary. The test
program assumes pin X3 on the Pyboard, pin 23 on ESP32 and pin 13 on ESP8266.
On the WeMos D1 Mini the equivalent pin is D7.

A remote using the NEC protocol is [this one](https://www.adafruit.com/products/389).

# 2. Installation and demo script

The receiver is a Python package. This minimises RAM usage: applications only
import the device driver for the protocol in use.


Copy the following to the target filesystem:
 1. `ir_rx` Directory and contents.

There are no dependencies.

The demo can be used to characterise IR remotes. It displays the codes returned
by each button. This can aid in the design of receiver applications. The demo
prints "running" every 5 seconds and reports any data received from the remote.

```python
from ir_rx.test import test
```
Instructions will be displayed at the REPL.

# 3. The driver

This implements a class for each supported protocol. Each class is subclassed
from a common abstract base class in `__init__.py`.

Applications should instantiate the appropriate class with a callback. The
callback will run whenever an IR pulse train is received. Example running on a
Pyboard:
```python
import time
from machine import Pin
from pyb import LED
from ir_rx.nec import NEC_8  # NEC remote, 8 bit addresses

red = LED(1)

def callback(data, addr, ctrl):
    if data < 0:  # NEC protocol sends repeat codes.
        print('Repeat code.')
    else:
        print('Data {:02x} Addr {:04x}'.format(data, addr))

ir = NEC_8(Pin('X3', Pin.IN), callback)
while True:
    time.sleep_ms(500)
    red.toggle()
```

#### Common to all classes

Constructor:  
Args:  
 1. `pin` is a `machine.Pin` instance configured as an input, connected to the
 IR decoder chip.  
 2. `callback` is the user supplied callback.
 3. `*args` Any further args will be passed to the callback.  

The user callback takes the following args:  
 1. `data` (`int`) Value from the remote. Normally in range 0-255. A value < 0
 signifies an NEC repeat code.
 2. `addr` (`int`) Address from the remote.
 3. `ctrl` (`int`) The meaning of this is protocol dependent:  
 NEC: 0  
 Philips: this is toggled 1/0 on repeat button presses. If the button is held
 down it is not toggled. The  transmitter demo implements this behaviour.  
 Sony: 0 unless receiving a 20-bit stream, in which case it holds the extended
 value.
 4. Any args passed to the constructor.

Bound variable:  
 1. `verbose=False` If `True` emits debug output.

Method:
 1. `error_function` Arg: a function taking a single `int` arg. If this is
 specified it will be called if an error occurs. The value corresponds to the
 error code (see below). Typical usage might be to provide some user feedback
 of incorrect reception although beware of occasional triggers by external
 events. In my testing the TSOP4838 produces 200µs pulses on occasion for no
 obvious reason. See [section 4](./RECEIVER.md#4-errors).

A function is provided to print errors in human readable form. This may be
invoked as follows:

```python
from ir_rx.print_error import print_error  # Optional print of error codes
# Assume ir is an instance of an IR receiver class
ir.error_function(print_error)
```
Class variables:
 1. These are constants defining the NEC repeat code and the error codes sent
 to the error function. They are discussed in [section 4](./RECEIVER.md#4-errors).

#### NEC classes

`NEC_8`, `NEC_16`

Typical invocation:
```python
from ir_rx.nec import NEC_8
```

Remotes using the NEC protocol can send 8 or 16 bit addresses. If the `NEC_16`
class receives an 8 bit address it will get a 16 bit value comprising the
address in bits 0-7 and its one's complement in bits 8-15.  
The `NEC_8` class enables error checking for remotes that return an 8 bit
address: the complement is checked and the address returned as an 8-bit value.
A 16-bit address will result in an error.

#### Sony classes

`SONY_12`, `SONY_15`, `SONY_20`

Typical invocation:
```python
from ir_rx.sony import SONY_15
```

The SIRC protocol comes in 3 variants: 12, 15 and 20 bits. `SONY_20` handles
bitstreams from all three types of remote. Choosing a class matching the remote
improves the timing reducing the likelihood of errors when handling repeats: in
20-bit mode SIRC timing when a button is held down is tight. A worst-case 20
bit block takes 39ms nominal, yet the repeat time is 45ms nominal.  
A single physical remote can issue more than one type of bitstream. The Sony
remote tested issued both 12 bit and 15 bit streams.

#### Philips classes

`RC5_IR`, `RC6_M0`

Typical invocation:
```python
from ir_rx.philips import RC5_IR
```

These support the RC-5 and RC-6 mode 0 protocols respectively.

# 4. Errors

IR reception is inevitably subject to errors, notably if the remote is operated
near the limit of its range, if it is not pointed at the receiver or if its
batteries are low. The user callback is not called when an error occurs.

On ESP8266 and ESP32 there is a further source of errors. This results from the
large and variable interrupt latency of the device which can exceed the pulse
duration. This causes pulses to be missed or their timing measured incorrectly.
On ESP8266 some improvment may be achieved by running the chip at 160MHz.

In general applications should provide user feedback of correct reception.
Users tend to press the key again if the expected action is absent.

In debugging a callback can be specified for reporting errors. The value passed
to the error function are represented by constants indicating the cause of the
error. These are driver ABC class variables and are as follows:

`BADSTART` A short (<= 4ms) start pulse was received. May occur due to IR
interference, e.g. from fluorescent lights. The TSOP4838 is prone to producing
200µs pulses on occasion, especially when using the ESP8266.  
`BADBLOCK` A normal data block: too few edges received. Occurs on the ESP8266
owing to high interrupt latency.  
`BADREP` A repeat block: an incorrect number of edges were received.  
`OVERRUN` A normal data block: too many edges received.  
`BADDATA` Data did not match check byte.  
`BADADDR` (`NEC_IR`) If `extended` is `False` the 8-bit address is checked
against the check byte. This code is returned on failure.  

# 5. Receiver platforms

Currently the ESP8266 suffers from [this issue](https://github.com/micropython/micropython/issues/5714).
Testing was therefore done without WiFi connectivity. If the application uses
the WiFi regularly, or if an external process pings the board repeatedly, the
crash does not occur.

Philips protocols (especially RC-6) have tight timing constraints with short
pulses whose length must be determined with reasonable accuracy. The Sony 20
bit protocol also has a timing issue in that the worst case bit pattern takes
39ms nominal, yet the repeat time is 45ms nominal. These issues can lead to
errors particularly on slower targets. As discussed above, errors are to be
expected. It is up to the user to decide if the error rate is acceptable.

Reception was tested using Pyboard D SF2W, ESP8266 and ESP32 with signals from
remote controls (where available) and from the tranmitter in this repo. Issues
are listed below.

NEC: No issues.  
Sony 12 and 15 bit: No issues.  
Sony 20 bit: On ESP32 some errors occurred when repeats occurred.  
Philips RC-5: On ESP32 with one remote control many errors occurred, but paired
with the transmitter in this repo it worked.  
Philips RC-6: No issues. Only tested against the transmitter in this repo.

# 6. Principle of operation

Protocol classes inherit from the abstract base class `IR_RX`. This uses a pin
interrupt to store in an array the time (in μs) of each transition of the pulse
train from the receiver chip. Arrival of the first edge starts a software timer
which runs for the expected duration of an IR block (`tblock`). The use of a
software timer ensures that `.decode` and the user callback can allocate.

When the timer times out its callback (`.decode`) decodes the data. `.decode`
is a method of the protocol specific subclass; on completion it calls the
`do_callback` method of the ABC. This resets the edge reception and calls
either the user callback or the error function (if provided). 

The size of the array and the duration of the timer are protocol dependent and
are set by the subclasses. The `.decode` method is provided in the subclass.

CPU times used by `.decode` (not including the user callback) were measured on
a Pyboard D SF2W at stock frequency. They were: NEC 1ms for normal data, 100μs
for a repeat code. Philips codes: RC-5 900μs, RC-6 mode 0 5.5ms.

# 7. References

[General information about IR](https://www.sbprojects.net/knowledge/ir/)

The NEC protocol:  
[altium](http://techdocs.altium.com/display/FPGA/NEC+Infrared+Transmission+Protocol)  
[circuitvalley](http://www.circuitvalley.com/2013/09/nec-protocol-ir-infrared-remote-control.html)

Philips protocols:  
[RC5](https://en.wikipedia.org/wiki/RC-5)  
[RC5](https://www.sbprojects.net/knowledge/ir/rc5.php)  
[RC6](https://www.sbprojects.net/knowledge/ir/rc6.php)

Sony protocol:  
[SIRC](https://www.sbprojects.net/knowledge/ir/sirc.php)

# Appendix 1 NEC Protocol description

A normal burst comprises exactly 68 edges, the exception being a repeat code
which has 4. An incorrect number of edges is treated as an error. All bursts
begin with a 9ms pulse. In a normal code this is followed by a 4.5ms space; a
repeat code is identified by a 2.25ms space. A data burst lasts for 67.5ms.

Data bits comprise a 562.5µs mark followed by a space whose length determines
the bit value. 562.5µs denotes 0 and 1.6875ms denotes 1.

In 8 bit address mode the complement of the address and data values is sent to
provide error checking. This also ensures that the number of 1's and 0's in a
burst is constant, giving a constant burst length of 67.5ms. In extended
address mode this constancy is lost. The burst length can (by my calculations)
run to 76.5ms.