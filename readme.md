# Shock controller

## Requirements

- [Shock Collar](https://www.amazon.com/gp/product/B07TDCWDRF)
- [YardStick One](https://greatscottgadgets.com/yardstickone/)
- python2
- [RFCat](https://github.com/atlas0fd00m/rfcat)

## Device registration

First you need to figure the collar transitter ID.

This can be done using rfcat:
Clone rfcat, build it and then run it
```
➜  rfcat git:(master) ✗ ./rfcat -r
No module named IPython.frontend.terminal.interactiveshell
'RfCat, the greatest thing since Frequency Hopping!'

Research Mode: enjoy the raw power of rflib

currently your environment has an object called "d" for dongle.  this is how 
you interact with the rfcat dongle:
```

Then execute

```python
d.ping()
d.setFreq(433000000)
d.setMdmModulation(MOD_ASK_OOK)
d.makePktFLEN(250)
d.RFxmit("HALLO")
d.RFrecv()
print(d.reprRadioConfig())
d.RFlisten()
```

Press some button on the remote, you will see some output like this:

```
Entering RFlisten mode...  packets arriving will be displayed on the screen
(press Enter to stop)
(1575149162.285) Received:  5464d28910001809cf  | Td.......
(1575149162.338) Received:  5464d28910001809cf  | Td.......
(1575149162.378) Received:  5464d28910001809cf  | Td.......
(1575149162.424) Received:  5464d28910001809cf  | Td.......
```

The transmitter id (or preamble) is `8910` in this case, so it's the characters 6 to 9.

Add this id to the `units` dictionairy in `server.py` like this:

```
units = {
    "display-name": rf.unhexlify('8910'),
}
```

## User registration

See the `authMap` dict in `server.py` and add your user+password and restrictions and desired.

## Running

- Run `server.py` using `python 2.7`.
- Open the website.
- ⚡️⚡️⚡️

### Notes
By default this server listens on all ipv6 interfaces and requires `https` using a `key.pem` and `cert.pem` in the same folder.
This can be disabled by removing the corresponding parameters.
