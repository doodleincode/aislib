#!/usr/bin/env python

"""
Simple AIS library.
This library supports creating and decoding NMEA formatted AIS type 1,5,24 messages

@author     Daniel Hong
https://github.com/doodleincode/aislib
This program is licensed under the GNU GENERAL PUBLIC LICENSE Version 2. 
A LICENSE file should have accompanied this program.
 
"""

import bitstring
import binascii
    
# Create a character encoding and reversed character encoding map which
# we will use to encode and decode, respectively, AIS bit streams

encodingchars = [
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?',
    '@', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 
    'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', "`", 'a', 'b', 'c', 'd', 'e', 'f', 'g',
    'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w'
]

# We'll populate this with the encoding chars k/v in reverse for use in decoding
# the AIS payload
re_encodingchars = {}

for i in range(len(encodingchars)):
    re_encodingchars[encodingchars[i]] = i

# END character encoding map

AISchars='@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_ !"#$%&\'()*+,-./0123456789:;<=>?'
re_AISchars = {}
for i in range(len(AISchars)):
    re_AISchars[AISchars[i]] = i

def AISString2Bits(name,length=20):
    if len(name)>length: name = name[:length]
    if len(name)<length: name = name+'@'*(length-len(name))
    return bitstring.Bits().join(['uint:6=%d' % re_AISchars[name[k]] for k in range(len(name))])

def int2bin6(num):
    """
    Converts the given integer to a 6-bit binary representation
    """
    
    return "".join(num & (1 << i) and '1' or '0' for i in range(5, -1, -1))

class CRCInvalidError(Exception):
    pass

class AISMessage(object):
    # Contain our AIS message elements
    _attrs = {}
    
    # Map the number of bits for each element in the AIS message
    _bitmap = {}
    
    def __init__(self, elements):
        # Init our bit mapping and load up default message values
        for key, arr in elements.iteritems():
            # arr[0] == data type of the element
            # arr[1] == number of bits for given element
            # arr[2] == the default value for the element
            self._bitmap[key] = [ arr[0], arr[1] ]
            
            # Set default value
            self.__setattr__(key, arr[2])
        
    def __getattr__(self, name):
        """
        We are overriding the behavior of __getattr__ to implement dynamic class
        properties. This way we can do stuff like [class].[property] without
        requiring a "getter" method for each property.
        
        If the AIS message element is not found in our attribute table, we'll
        revert to the default behavior of __getattr__
        """
        
        if name in self._attrs:
            return self._attrs[name]
        
        # Preserve the default behavior if our custom attributes were not found
        return super(AISMessage, self).__getattr__(name)
        
    def __setattr__(self, name, value):
        """
        We are overriding the __setattr__ to implement dynamic property "setters".
        """
        
        if type(value) not in [ int,long]:
            raise TypeError("Value must be an integer.")
            
        if name == "_bitmap":
            super(AISMessage, self).__setattr__(name, value)
            
        # Set attributes that are supported by the sub-classed AIS message type
        elif name in self._bitmap:
            # String format is: [datatype]:[num_bits]=[value]
            self._attrs[name] = bitstring.Bits(
                    "%s:%d=%d" % (self._bitmap[name][0], self._bitmap[name][1], value))

        else:
            raise AttributeError("Unsupported AIS message element.")
    
    def get_attr(self, name):
        """
        Returns an integer representation of the binary value for the given 
        element name.
        
        @param  name    Name of the AIS message element to retrieve
        @return         Human readable int value. If invalid element, returns None
        """
        
        if name in self._attrs:
            if self._bitmap[name][0] == "int":
                return self._attrs[name].int
            else:
                return self._attrs[name].uint
            
        return None
        
    ## Sub-classes should implement the methods below ##
    
    def build_bitstream(self):
        """
        Build the bitstream which we will be using to encode the payload. This will
        basically involve concatenating all the message elements into one bitstring.
        
        Sub-classes that extend the AISMessage class are required to implement this
        method. Example implementation:
        
            return bitstring.Bits().join([
                self.element_1, self.element_2, [...]
            ])
        """
        pass
    
    def unpack(self, bitstream):
        """
        Unpack a bitstream into AIS message elements. Sub-classes can optionally
        implement this method to support decoding of AIS messages. Example
        implementation:
            
            self._attrs["element_1"] = bitstring.Bits(bin=bitstream[0:6])
            self._attrs["element_2"] = bitstring.Bits(bin=bitstream[6:8])
            [...]
        """
        pass
        
class AISPositionReportMessage(AISMessage):
    def __init__(self, id=1, repeat=0, mmsi=0, status=15, rot=-128, sog=0, pa=0,
                       lon=0, lat=0, cog=3600, heading=511, ts=60, smi=0, spare=0, 
                       raim=0, comm_state=0):
        """
        Returns an instance of an AIS Position Report Message class
        The parameters contain the default values, simply set the parameters
        who's value need to change. Ex:
            
            aismsg = AISPositionReportMessage(mmsi=12345, lon=4567, lat=5432)
        """
        
        super(AISPositionReportMessage, self).__init__({
                    # message_element : ["data_type", num_bits, initial_value]
                    'id'        : ["uint", 6, id], 
                    'repeat'    : ["uint", 2, repeat], 
                    'mmsi'      : ["uint", 30, mmsi], 
                    'status'    : ["uint", 4, status], 
                    'rot'       : ["int", 8, rot], 
                    'sog'       : ["uint", 10, sog], 
                    'pa'        : ["uint", 1, pa], 
                    'lon'       : ["int", 28, lon], 
                    'lat'       : ["int", 27, lat], 
                    'cog'       : ["uint", 12, cog], 
                    'heading'   : ["uint", 9, heading], 
                    'ts'        : ["uint", 6, ts], 
                    'smi'       : ["uint", 2, smi], 
                    'spare'     : ["uint", 3, spare], 
                    'raim'      : ["uint", 1, raim], 
                    'comm_state' : ["uint", 19, comm_state]
                })
    
    def build_bitstream(self):
        return bitstring.Bits().join([
            self.id,
            self.repeat,
            self.mmsi,
            self.status,
            self.rot,
            self.sog,
            self.pa,
            self.lon,
            self.lat,
            self.cog,
            self.heading,
            self.ts,
            self.smi,
            self.spare,
            self.raim,
            self.comm_state
        ])
    
    def unpack(self, bitstream):
        # TODO: figure out a better way to do this, but works fine for now
        self._attrs["id"]       = bitstring.Bits(bin=bitstream[0:6])
        self._attrs["repeat"]   = bitstring.Bits(bin=bitstream[6:8])
        self._attrs["mmsi"]     = bitstring.Bits(bin=bitstream[8:38])
        self._attrs["status"]   = bitstring.Bits(bin=bitstream[38:42])
        self._attrs["rot"]      = bitstring.Bits(bin=bitstream[42:50])
        self._attrs["sog"]      = bitstring.Bits(bin=bitstream[50:60])
        self._attrs["pa"]       = bitstring.Bits(bin=bitstream[60:61])
        self._attrs["lon"]      = bitstring.Bits(bin=bitstream[61:89])
        self._attrs["lat"]      = bitstring.Bits(bin=bitstream[89:116])
        self._attrs["cog"]      = bitstring.Bits(bin=bitstream[116:128])
        self._attrs["heading"]  = bitstring.Bits(bin=bitstream[128:137])
        self._attrs["ts"]       = bitstring.Bits(bin=bitstream[137:143])
        self._attrs["smi"]      = bitstring.Bits(bin=bitstream[143:145])
        self._attrs["spare"]    = bitstring.Bits(bin=bitstream[145:148])
        self._attrs["raim"]     = bitstring.Bits(bin=bitstream[148:149])
        self._attrs["comm_state"] = bitstring.Bits(bin=bitstream[149:168])
            

class AISStaticAndVoyageReportMessage(AISMessage):
    def __init__(self, id=5, repeat=0, mmsi=0, ais_version=0, imo=0, callsign=0, shipname=0,
                       shiptype=0, to_bow=0, to_stern=0, to_port=0, to_starboard=0, epfd=1,
                       month=0, day=0, hour=24, minute=60, draught=0,
                       destination=0, dte=0, spare=0):
        """
        Returns an instance of an AIS Position Report Message class
        The parameters contain the default values, simply set the parameters
        who's value need to change. Ex:
            
            aismsg = AISStaticAndVoyageReportMessage(mmsi=12345,shipname='ASIAN JADE')
        """
        
        super(AISStaticAndVoyageReportMessage, self).__init__({
                    # message_element : ["data_type", num_bits, initial_value]
                    'id'           : ["uint", 6, id], 
                    'repeat'       : ["uint", 2, repeat], 
                    'mmsi'         : ["uint", 30, mmsi], 
                    'ais_version'  : ["uint", 2, ais_version], 
                    'imo'          : ["uint", 30, imo], 
                    'callsign'     : ["uint", 42, AISString2Bits(callsign,length=42/6).int if type(callsign) == str else callsign], 
                    'shipname'     : ["uint", 120, AISString2Bits(shipname,length=120/6).int if type(shipname) == str else shipname], 
                    'shiptype'     : ["uint", 8, shiptype], 
                    'to_bow'       : ["uint", 9, to_bow], 
                    'to_stern'     : ["uint", 9, to_stern], 
                    'to_port'      : ["uint", 6, to_port], 
                    'to_starboard' : ["uint", 6, to_starboard], 
                    'epfd'         : ["uint", 4, epfd], 
                    'month'        : ["uint", 4, month], 
                    'day'          : ["uint", 5, day], 
                    'hour'         : ["uint", 5, hour], 
                    'minute'       : ["uint", 6, minute], 
                    'draught'      : ["uint", 8, draught], 
                    'destination'  : ["uint", 120, AISString2Bits(destination,length=120/6).int if type(destination) == str else destination], 
                    'dte'          : ["uint", 1, dte], 
                    'spare'        : ["uint", 1, spare]
                })
    
    def build_bitstream(self):
        return bitstring.Bits().join([
            self.id,
            self.repeat,
            self.mmsi,
            self.ais_version,
            self.imo,
            self.callsign,
            self.shipname,
            self.shiptype,
            self.to_bow,
            self.to_stern,
            self.to_port,
            self.to_starboard,
            self.epfd,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.draught,
            self.destination,
            self.dte,
            self.spare
        ])
    
    def unpack(self, bitstream):
        # TODO: figure out a better way to do this, but works fine for now
        self._attrs["id"]       = bitstring.Bits(bin=bitstream[0:6])
        self._attrs["repeat"]   = bitstring.Bits(bin=bitstream[6:8])
        self._attrs["mmsi"]     = bitstring.Bits(bin=bitstream[8:38])
        self._attrs["ais_version"]   = bitstring.Bits(bin=bitstream[38:40])
        self._attrs["imo"]      = bitstring.Bits(bin=bitstream[40:70])
        self._attrs["callsign"]      = bitstring.Bits(bin=bitstream[70:112])
        self._attrs["shipname"]       = bitstring.Bits(bin=bitstream[112:232])
        self._attrs["shiptype"]      = bitstring.Bits(bin=bitstream[232:240])
        self._attrs["to_bow"]      = bitstring.Bits(bin=bitstream[240:249])
        self._attrs["to_stern"]      = bitstring.Bits(bin=bitstream[249:258])
        self._attrs["to_port"]  = bitstring.Bits(bin=bitstream[258:264])
        self._attrs["to_starboard"]       = bitstring.Bits(bin=bitstream[264:270])
        self._attrs["epfd"]      = bitstring.Bits(bin=bitstream[270:274])
        self._attrs["month"]    = bitstring.Bits(bin=bitstream[274:278])
        self._attrs["day"]     = bitstring.Bits(bin=bitstream[278:283])
        self._attrs["hour"]     = bitstring.Bits(bin=bitstream[283:288])
        self._attrs["minute"]     = bitstring.Bits(bin=bitstream[288:294])
        self._attrs["draught"]     = bitstring.Bits(bin=bitstream[294:302])
        self._attrs["destination"]     = bitstring.Bits(bin=bitstream[302:422])
        self._attrs["dte"]     = bitstring.Bits(bin=bitstream[422:423])
        self._attrs["spare"] = bitstring.Bits(bin=bitstream[423:424])
            
class AISStaticDataReportAMessage(AISMessage):
    def __init__(self, id=24, repeat=0, mmsi=0, partno=0, shipname=0, spare=0):
        """
        Returns an instance of an AIS Static Data Report Message Format A class
        The parameters contain the default values, simply set the parameters
        whose values need to change. Ex:
            
            aismsg = AISPositionReportAMessage(mmsi=12345, shipname='ASIAN JADE')
        """
        
        super(AISStaticDataReportAMessage, self).__init__({
                    # message_element : ["data_type", num_bits, initial_value]
                    'id'              : ["uint", 6, id], 
                    'repeat'          : ["uint", 2, repeat], 
                    'mmsi'            : ["uint", 30, mmsi], 
                    'partno'          : ["uint", 2, partno], 
                    'shipname'        : ["uint", 120, AISString2Bits(shipname,length=120/6).int if type(shipname) == str else shipname], 
                    'spare'           : ["uint", 8, spare]
                })
    
    def build_bitstream(self):
        return bitstring.Bits().join([
            self.id,
            self.repeat,
            self.mmsi,
            self.partno,
            self.shipname,
            self.spare
        ])
    
    def unpack(self, bitstream):
        # TODO: figure out a better way to do this, but works fine for now
        self._attrs["id"]       = bitstring.Bits(bin=bitstream[0:6])
        self._attrs["repeat"]   = bitstring.Bits(bin=bitstream[6:8])
        self._attrs["mmsi"]     = bitstring.Bits(bin=bitstream[8:38])
        self._attrs["partno"]   = bitstring.Bits(bin=bitstream[38:40])
        self._attrs["shipname"]      = bitstring.Bits(bin=bitstream[40:160])
        self._attrs["spare"]      = bitstring.Bits(bin=bitstream[160:168])
        

class AISStaticDataReportBMessage(AISMessage):
    def __init__(self, id=24, repeat=0, mmsi=0, partno=1, shiptype=0,
                       vendorid=0,model=0,serial=0,callsign=0,
                       to_bow=0,to_stern=0,to_port=0,to_starboard=0,
                       spare=0):
        """
        Returns an instance of an AIS Static Data Report Message Format A class
        The parameters contain the default values, simply set the parameters
        whose values need to change. Ex:
            
            aismsg = AISPositionReportBMessage(mmsi=12345, shiptype=60)
        """
        
        super(AISStaticDataReportBMessage, self).__init__({
                    # message_element : ["data_type", num_bits, initial_value]
                    'id'              : ["uint", 6, id], 
                    'repeat'          : ["uint", 2, repeat], 
                    'mmsi'            : ["uint", 30, mmsi], 
                    'partno'          : ["uint", 2, partno], 
                    'shiptype'        : ["uint", 8, shiptype], 
                    'vendorid'        : ["uint", 18, AISString2Bits(vendorid,length=18/6).int if type(vendorid) == str else vendorid], 
                    'model'           : ["uint", 4, model], 
                    'serial'          : ["uint", 20, serial], 
                    'callsign'        : ["uint", 42, AISString2Bits(callsign,length=42/6).int if type(callsign) == str else callsign], 
                    'to_bow'          : ["uint", 9, to_bow], 
                    'to_stern'        : ["uint", 9, to_stern], 
                    'to_port'         : ["uint", 6, to_port], 
                    'to_starboard'    : ["uint", 6, to_starboard], 
                    'spare'           : ["uint", 6, spare]
                })
    
    def build_bitstream(self):
        return bitstring.Bits().join([
            self.id,
            self.repeat,
            self.mmsi,
            self.partno,
            self.shiptype,
            self.vendorid,
            self.model,
            self.serial,
            self.callsign,
            self.to_bow,
            self.to_stern,
            self.to_port,
            self.to_starboard,
            self.spare
        ])
    
    def unpack(self, bitstream):
        # TODO: figure out a better way to do this, but works fine for now
        self._attrs["id"]       = bitstring.Bits(bin=bitstream[0:6])
        self._attrs["repeat"]   = bitstring.Bits(bin=bitstream[6:8])
        self._attrs["mmsi"]     = bitstring.Bits(bin=bitstream[8:38])
        self._attrs["partno"]   = bitstring.Bits(bin=bitstream[38:40])
        self._attrs["shiptype"] = bitstring.Bits(bin=bitstream[40:48])
        self._attrs["vendorid"] = bitstring.Bits(bin=bitstream[48:66])
        self._attrs["model"]    = bitstring.Bits(bin=bitstream[66:70])
        self._attrs["serial"]   = bitstring.Bits(bin=bitstream[70:90])
        self._attrs["callsign"] = bitstring.Bits(bin=bitstream[90:132])
        self._attrs["to_bow"]   = bitstring.Bits(bin=bitstream[132:141])
        self._attrs["to_stern"] = bitstring.Bits(bin=bitstream[141:150])
        self._attrs["to_port"]  = bitstring.Bits(bin=bitstream[150:156])
        self._attrs["to_starboard"]  = bitstring.Bits(bin=bitstream[156:162])
        self._attrs["spare"]      = bitstring.Bits(bin=bitstream[162:168])
        
class AIS(object):
    # Instance of the AISMessage class
    _ais_message = None
    
    def __init__(self, ais_message):
        # If the provided param was not an AISMessage object, throw exception
        if not isinstance(ais_message, AISMessage):
            raise TypeError("Variable 'ais_message' is not an instance of 'AISMessage'.")
            
        # Otherwise set the variable
        self._ais_message = ais_message
        
    def build_payload(self, invert_crc = False):
        """
        Builds the AIS NMEA message string
        This method only supports AIVDM, single fragment, 168 bit (28-char) payload
        Type 1 and Type 24 format A are of this kind
        
        Field 1, !AIVDM, identifies this as an AIVDM packet.

        Field 2 (1) is the count of fragments in the currently accumulating message.
        The payload size of each sentence is limited by NMEA 0183's 82-character maximum, 
        so it is sometimes required to split a payload over several fragment sentences.

        Field 3 (1) is the fragment number of this sentence. It will be one-based. 
        A sentence with a fragment count of 1 and a fragment number of 1 is complete in itself.

        Field 4 (empty) is a sequential message ID for multi-sentence messages.

        Field 5 (A) is a radio channel code. AIS uses the high side of the duplex 
        from two VHF radio channels: 
        - AIS Channel A is 161.975Mhz (87B); 
        - AIS Channel B is 162.025Mhz (88B).
        
        Field 6 is the encoded payload string
        
        Field 7 (0) is the number of fill bits requires to pad the data payload 
        to a 6-bit boundary. This value can range from 1-5.
        """
        
        payLoad =  self.encode() 
        payload = "!AIVDM,1,1,,A," + payLoad + '*'
        chksum = self.crc(payload)
        
        if invert_crc:
            chksum = ~chksum

        return payload + "%02X" % (chksum & 0xff)
        
    def encode(self, bitstr = None):
        """
        Encode a bitstream into a 6-bit encoded AIS message string
        
        @param  bitstr  The bitstream. This should be a Bit object generated 
                        from bitstring.Bit(...). If this is not provided, then
                        it will use the bitstring from the '_ais_message' property
        @return         6-bit encoded AIS string
        """
        
        curr_index = 0
        curr_offset = 6     # We'll be encoding 6 bits at a time
        encoded_str = []
        
        if bitstr == None:
            bitstr = self._ais_message.build_bitstream()
        
        # The total AIS message is len(bitstr) bits
        # Since we are encoding 6-bit chunks, we are looping
        #  round(len(bitstr)/ 6.) times (type 5 has 424 bits which does not divide by 6
       #print len(bitstr),len(bitstr)/6,len(bitstr)/6.,int(round(len(bitstr)/6.))
        for i in range(0, int(round(len(bitstr)/6.))):
            block = bitstr[curr_index:curr_offset]
            encoded_str.append(encodingchars[block.uint])
            curr_index += 6
            curr_offset += 6
        remainingbits = len(bitstr) %6
        fillbits = (6 -remainingbits) if remainingbits !=0 else 0

        return ("".join(encoded_str))+','+chr(ord('0')+fillbits)
    def decode(self, msg):
        """
        Decodes an AIS NMEA formatted message. Currently only supports the 
        Position Report Message type. On success, returns an instance of 
        AISPositionReportMessage. A CRC check is performed. If the CRC does not 
        match, a CRCInvalidError exception is thrown
        
        @param  msg     The message to decode
        @return         If CRC checks, returns an instance of AISPositionReportMessage
        """
        
        computed_crc = self.crc(msg)
        given_crc = int(msg[-2:], 16)
        
        # If CRC did not match, throw exception!
        if given_crc != computed_crc:
            raise CRCInvalidError("The given CRC did not match the computed CRC.")
            
        # Otherwise we can continue with decoding the message
        # ...
        
        # Grap just the payload. The 6th index in the AIS message contains the payload
        payload,fillbits = msg.split(",")[5:7]
        
        # First we will reverse the 6-bit ascii encoding to its integer equivalent
        # using our reverse encoded character map
        dec = []
        
        for c in payload:
            dec.append(re_encodingchars[c])
        
        # Now we will take our list of integers and convert it to a bitstream
        bits = []
        
        for i in range(len(dec)):
            bits.append(int2bin6(dec[i]))
            
        bitstream = "".join(bits)
        if fillbits[0] !='0':bitstream = bitstream[:-int(fillbits[0])]
        msgId = bitstream[0:6]#;print msgId
        if   msgId == '000001':
             aismsg = AISPositionReportMessage()
        elif msgId == '011000' and bitstream[38] == '0':
             aismsg = AISStaticDataReportAMessage()
        elif msgId == '011000' and bitstream[38] == '1':
             aismsg = AISStaticDataReportBMessage()
        elif msgId == '000101':
             aismsg = AISStaticAndVoyageReportMessage()
        aismsg.unpack(bitstream)
        return aismsg
    
    def crc(self, msg):
        """
        Generates the CRC for the given AIS NMEA formatted string
        
        @param  msg     The message used to generate the CRC. This should be
                        a well formed NMEA formatted message
        @return         Integer representation of the CRC. You can use hex(crc)
                        to get the hex
        """
        
        chksum = 0
        
        # If the input contains the entire NMEA message, then we just need to
        # get the string between the ! and *
        # Otherwise we'll assume the input contains just the string to checksum
        astk = msg.rfind("*")
        
        if msg[0] == "!" and astk != -1:
            msg = msg[1:astk]
        
        for c in msg:
            chksum = chksum ^ ord(c)
            
        return chksum

