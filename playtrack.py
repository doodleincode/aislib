import aislib
import time
import sys
ships={'kornaros':(239311000,'kornaros.txt','!AIVDM,1,1,,A,53T>HV01hAoM=PqP001HUA<DqA`u>0du8p58u<0t891::40Ht;@00000000000000000000,2*04'),
       'highspeed4':(239658000,'highspeed4.txt','!AIVDM,1,1,,A,53TST402<`;M=L`@000PTLQ=0DDB3@000000000`5hf<<40Ht7P00000000000000000000,2*1D'),
       'venizelos':(237628000,'venizelos.txt','!AIVDM,1,1,,A,53RWbH01pbEU=MM`000DjqHDpU`Dhu<00000000t:iF>>40HtAP00000000000000000000,2*58'),
       'knossos':(237641000,'knossos.txt','!AIVDM,1,1,,A,53R`M:02<LEu=U4t000dpu=<u>104h4<D000000t=Ic==40HtA000000000000000000000,2*2D')}
def main():   
  ship='knossos'
  if len(sys.argv)>1: ship=sys.argv[1]
  try: print ships[ship][2]
  except: pass
  f=open(ships[ship][1])
  l=f.readline()
  for l in f:
    try:
        fields=l.split('\t')
        lat=float(fields[3])
        lon=float(fields[4])
        sog=float(fields[2])
        cog=float(fields[5])
    except ValueError:
        print >> sys.stderr,l,
        continue
    aismsg = aislib.AISPositionReportMessage(
        mmsi =ships[ship][0],
        pa = 1,
        lon = int((lon)*60*10000),
        lat = int((lat)*60*10000),
        heading =int(cog),
        sog = int(sog*10),
        cog = int(cog*10),
        status = 0,
        ts = 60,
        raim = 1,
        comm_state = 82419   
    )
    ais = aislib.AIS(aismsg)
    payload = ais.build_payload(False)
    print payload
    time.sleep(2)
#   print "nav status: %d" % aismsg.get_attr("status")
    
    aismsg2 = ais.decode(payload)
    ais2 = aislib.AIS(aismsg2)
    payload2 = ais2.build_payload(False)
#   print payload2
#   print "nav status: %d" % aismsg2.get_attr("status")
    
    #print aismsg.id
    #print aismsg.repeat
    
    #bitstr = aismsg.build_bitstream() 
    #print bitstr.bin
  # #print bitstr.len
  f.close()
if __name__ == "__main__":
    main()
