import time
from config import CORE2AND, header, tail, dataCode
from customcrc16 import CRC16_CCITTFALSE
from utils import utils

class commandPalette():
    
    def makeLen(self, data):
        abs_length : int = hex(len(data))
        lenlen = len(abs_length)
        
        if lenlen <= 4:
            if len(abs_length)==3:
                abs_length = abs_length[0:2] + "0" + abs_length[-1]
            len_h, len_l = '0x00', abs_length
            
        elif 4 < lenlen and lenlen <=6:
            if len(abs_length)==5:
                abs_length = abs_length[0:2] + "0" + abs_length[2:]
            len_h, len_l = abs_length[0:4], '0x'+abs_length[4:]
            
        return len_h, len_l
    
    def makeCMD(self, cmd):
        if cmd == "connect":
            data = dataCode.connect
        elif cmd == "userinfo":
            data = dataCode.userinfo
        elif cmd == "userinfo":
            data = dataCode.userinfo
            
        dircode = CORE2AND      
        localheader = header
        localheader[1], localheader[2] = self.makeLen(data); localheader[3] = dircode
            
        return localheader, data