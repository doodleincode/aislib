from __future__ import print_function

import aislib
#
# Tests for Message Type 1
#
aismsg = aislib.AISPositionReportMessage(
    mmsi = 237772000,
    status = 8,
    sog = 75,
    pa = 1,
    lon = (25*60+00)*10000,
    lat = (35*60+30)*10000,
    cog = 2800,
    ts = 40,
    raim = 1,
    comm_state = 82419   
)
ais = aislib.AIS(aismsg)
payload = ais.build_payload(False)
print(payload)
print("nav status: %d" % aismsg.get_attr("status"))

aismsg2 = ais.decode(payload)
ais2 = aislib.AIS(aismsg2)
payload2 = ais2.build_payload(False)
assert payload ==  payload2
print("nav status: %d" % aismsg2.get_attr("status"))

#print aismsg.id
#print aismsg.repeat

#bitstr = aismsg.build_bitstream() 
#print bitstr.bin
#print bitstr.len

# 
# Tests for Message Type 24 Format A
#
del aismsg
del aismsg2
#print aislib.AISString2Bits('ABC')
aismsg = aislib.AISStaticDataReportAMessage(mmsi=237772000,shipname=aislib.AISString2Bits('OF THE HIGH SEAS').int)
aismsg = aislib.AISStaticDataReportAMessage(mmsi=237772000,shipname='OF THE HIGH SEAS')
ais = aislib.AIS(aismsg)
payload = ais.build_payload(False)
print(payload)
aismsg2 = ais.decode(payload)
ais2 = aislib.AIS(aismsg2)
payload2 = ais2.build_payload(False)
assert payload ==  payload2

# 
# Tests for Message Type 24 Format B
#
aismsg = aislib.AISStaticDataReportBMessage(mmsi=237772000,shiptype=36,
         vendorid='DIY',
         callsign='SVXYZ',
         to_bow=5,to_stern=5,to_port=1,to_starboard=1)
ais = aislib.AIS(aismsg)
payload = ais.build_payload(False)
print(payload)
aismsg2 = ais.decode(payload)
ais2 = aislib.AIS(aismsg2)
payload2 = ais2.build_payload(False)
assert payload ==  payload2

# 
# Tests for Message Type 5
#
print(' Tests for Message Type 5')
aismsg = aislib.AISStaticAndVoyageReportMessage(mmsi=237772000,
         imo=0, 
         callsign='SVXYZ',
         shipname='OF THE HIGH SEAS',
         shiptype=36,
         to_bow=5,to_stern=5,to_port=1,to_starboard=1, draught=10,
         epfd=1, month=5, day=14, hour=20, minute=15,
         destination='STROFADES')
ais = aislib.AIS(aismsg)
payload = ais.build_payload(False)
print(payload)
aismsg2 = ais.decode(payload)
ais2 = aislib.AIS(aismsg2)
payload2 = ais2.build_payload(False)
assert payload ==  payload2
