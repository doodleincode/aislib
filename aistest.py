import aislib
#
# Tests for Message Type 1
#
aismsg = aislib.AISPositionReportMessage(
    mmsi = 205344990,
    pa = 1,
    lon = 2644228,
    lat = 30737782,
    cog = 1107,
    ts = 40,
    raim = 1,
    comm_state = 82419   
)
ais = aislib.AIS(aismsg)
payload = ais.build_payload(False)
print payload
print "nav status: %d" % aismsg.get_attr("status")

aismsg2 = ais.decode(payload)
ais2 = aislib.AIS(aismsg2)
payload2 = ais2.build_payload(False)
print payload2
print "nav status: %d" % aismsg2.get_attr("status")

#print aismsg.id
#print aismsg.repeat

#bitstr = aismsg.build_bitstream() 
#print bitstr.bin
#print bitstr.len

# 
# Tests for Message Type 24 Format A
#
print aislib.AISString2Bits('ABC')
aismsg = aislib.AISStaticDataReportAMessage(mmsi=237772000,shipname=aislib.AISString2Bits('OF THE HIGH SEAS').int)
ais = aislib.AIS(aismsg)
payload = ais.build_payload(False)
print payload
aismsg2 = ais.decode(payload)
ais2 = aislib.AIS(aismsg2)
payload2 = ais2.build_payload(False)
print payload2

# 
# Tests for Message Type 24 Format B
#
aismsg = aislib.AISStaticDataReportBMessage(mmsi=237772000,shiptype=60,
         vendorid=aislib.AISString2Bits('DIY',length=3).int,
         callsign=aislib.AISString2Bits('SVXYZ',length=7).int,
         to_bow=5,to_stern=5,to_port=1,to_starboard=1)
ais = aislib.AIS(aismsg)
payload = ais.build_payload(False)
print payload
aismsg2 = ais.decode(payload)
ais2 = aislib.AIS(aismsg2)
payload2 = ais2.build_payload(False)
print payload2
