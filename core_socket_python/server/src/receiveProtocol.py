import json
from config import AND2CORE
from config import dataCode
from customcrc16 import CRC16_CCITTFALSE
from utils import utils

    
class recvAndroid2Core():
    def __init__(self):
        self.util = utils()
        self.crcagent = CRC16_CCITTFALSE()
    
    def breakMessage(self, msg : str):
        data : list= msg.split(',')
        return data
    
    def parseConnect(self, msg_list : list):
        if msg_list[3] == "START":
            return True #call 0x23, CONNECT message
        else:
            return False
    
    def parseOBUdata(self, msg_list : list):
        dictdata = {
            msg_list[3] : msg_list[4],
            msg_list[5] : msg_list[6]
        }
        jsondata = json.dumps(dictdata, indent=2, ensure_ascii=False)
        return jsondata
    
    def parseREQuser(self, msg_list : list):
        if msg_list[3] == "PNUM" or "QRCODE": # suppose request on msg_list[3]
            dictdata = {
                msg_list[3] : msg_list[4],
            }
            jsondata = json.dumps(dictdata, indent=2, ensure_ascii=False)
            return jsondata # call 0x23, PROD-INFO message for msg_list[3]
        else:
            return False
        
    def parsePayinfo(self, msg_list : list):
        method = msg_list[3]
        if method == "CARD":
            dictdata = {
                "PROC-CODE" : msg_list[4],
                "CARD-NUM" : msg_list[5],
                "PRICE" : msg_list[6],
                "TAX" : msg_list[7],
                "APPROVAL-NUM" : msg_list[8],
                "APPROVAL-DT" : msg_list[9],
                "AQCUIRER-NUM" : msg_list[10],
                "CARDCO-NUM" : msg_list[11]
            }
            
            jsondata = json.dumps(dictdata, indent=2, ensure_ascii=False)
            return  jsondata
        elif method == "YPAY":
            return method
        else:
            return False 
    
    def protoDecoder(self, msg : str):
        msg_list = self.breakMessage(msg)
        msg_header = msg_list[2]
        print(msg_list)
        
        if msg_header == dataCode.connect:
            return msg_header,self.parseConnect(msg_list)
            
        elif msg_header == dataCode.obudata:
            print("this is a obu message")
            jsondata = self.parseOBUdata(msg_list)
            return msg_header, jsondata
            
        elif msg_header == dataCode.requser:
            ret = self.parseREQuser(msg_list)
            if ret != False:
                return msg_header, ret
            else:
                return ret
            
        elif msg_header == dataCode.prodinfo:
            if msg_list[3] == "REQ": # suppose request on msg_list[4]
                return True, msg_list[4] # call 0x23, PROD-INFO message for msg_list[4]
            else:
                return False
            
        elif msg_header == dataCode.payinfo:
            ret = self.parsePayinfo(msg_list)
            if ret != False:
                return msg_header, ret
            else:
                return ret                 
            
        else:
            SyntaxError("invalid msg")
            

if __name__ == "__main__":
    connectmsg = '0x02,0x32,CONNECT,START,crc,crc,0x03'
    obumsg = "0x02,0x12,OBU-DATA,OBU-INFO,21352436531,ISSUE-INFO,3252421,crc,crc,0x03"
    requsermsg = '0x02,0x32,REQ-USER,PNUM,01028760427,crc,crc,0x03'
    prodinfomsg = '0x02,0x32,PROD-INFO,REQ,EEVEE,crc,crc,0x03'
    payinfomsgCARD = '0x02,0x32,PAY-INFO,CARD,0000,465411,524500,47681,0123456,20230313,05,018,crc,crc,0x03'
    payinfomsgYPAY = '0x02,0x32,PAY-INFO,YPAY,crc,crc,0x03'
    
    # dummy test
    cuagent = recvAndroid2Core()
    header, jsondata = cuagent.protoDecoder(connectmsg)
    print(header, jsondata)
    print("--------------")
    header, jsondata = cuagent.protoDecoder(obumsg)
    print(header, jsondata)
    print("--------------")
    header, jsondata = cuagent.protoDecoder(requsermsg)
    print(header, jsondata)
    print("--------------")
    header, jsondata = cuagent.protoDecoder(prodinfomsg)
    print(header, jsondata)
    print("--------------")
    header, jsondata = cuagent.protoDecoder(payinfomsgCARD)
    print(header, jsondata)
    print("--------------")
    header, jsondata = cuagent.protoDecoder(payinfomsgYPAY)
    print(header, jsondata)
    print("--------------")
    