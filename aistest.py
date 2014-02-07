import aislib

def main():   
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

if __name__ == "__main__":
    main()
