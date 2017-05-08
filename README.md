aislib
======

A Python library for decoding and encoding: 
 * AIS type 1 messages
 * AIS type 24 part A and Part B (main craft case )

The bitstring Python library is a required dependency. You can get it here: https://pypi.python.org/pypi/bitstring

TODO
------

* Still need to implement the communication state bits. These bits are divided into three sections:
  * bits 1-2 is the "sync state"
  * bits 3-5 is the "slot time-out"
  * bits 6-19 is the "sub message"
