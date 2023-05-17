import json
from .config import dataCode
# from customcrc16 import CRC16_CCITTFALSE
from .utils import utils

    
class recvAndroid2Core():
    def __init__(self):
        self.util = utils()
        # self.crcagent = CRC16_CCITTFALSE()
    
    async def breakMessage(self, msg : str):
        data : list= msg.split(',')
        return data
    
    async def parseConnect(self, msg_list : list):
        dictdata = {"state": msg_list[1]}
        jsondata = json.dumps(dictdata, indent=2, ensure_ascii=False)
        return jsondata
    
    async def parseOBUdata(self, msg_list : list):
        dictdata = {
            msg_list[1] : msg_list[2],
            msg_list[3] : msg_list[4]
        }
        jsondata = json.dumps(dictdata, indent=2, ensure_ascii=False)
        return jsondata
    
    async def parseREQuser(self, msg_list : list):
        if msg_list[1] == "user_idx":
            dictdata = {
                msg_list[1] : msg_list[2],
            }
            jsondata = json.dumps(dictdata, indent=2, ensure_ascii=False)
            return jsondata # call 0x23, PROD-INFO message for msg_list[3]
        else:
            return False
        
    async def parsePayinfo(self, msg_list : list):
        method = msg_list[1]
        if method == "CARD":
            dictdata = {}
            numdata = len(msg_list) - 5
            for i in range(numdata//2):
               dictdata[msg_list[2+i*2]] = msg_list[2+i*2+1]
            jsondata = json.dumps(dictdata, indent=2, ensure_ascii=False)
            return  jsondata
        elif method == "YPAY":
            return method
        else:
            return False

    async def parseUserInfo(self, msg_list : list):
        # if msg_list[1] == "not_registered_obu":
        #     ...
        # elif msg_list[1] == "not_registered_user":
        #     ...
        # elif msg_list[1] == "diff_obu":
        #     ...
        # else:
        dictdata = {"param1":msg_list[1],
                    "param2":msg_list[2]}

        jsondata = json.dumps(dictdata, indent=2, ensure_ascii=False)
        return jsondata
    
    async def protoDecoder(self, msg : str):
        msg_list = await self.breakMessage(msg)
        msg_header = msg_list[0]
        print("msg_list:",msg_list)
        
        if msg_header == dataCode.connect:
            ret = await self.parseConnect(msg_list)
            return msg_header, ret
            
        elif msg_header == dataCode.obudata:
            print("this is a obu message")
            jsondata = await self.parseOBUdata(msg_list)
            return msg_header, jsondata
            
        elif msg_header == dataCode.requser:
            ret = await self.parseREQuser(msg_list)
            if ret != False:
                return msg_header, ret
            else:
                return ret
            
        elif msg_header == dataCode.prodinfo:
            if msg_list[3] == "REQ": # suppose request on msg_list[4]
                return True, msg_list[2] # call 0x23, PROD-INFO message for msg_list[4]
            else:
                return False
            
        elif msg_header == dataCode.payinfo:
            ret = await self.parsePayinfo(msg_list)
            if ret != False:
                return msg_header, ret
            else:
                return ret                 

        elif msg_header == dataCode.userinfo:
            ret = await self.parseUserInfo(msg_list)
            if ret != False:
                return msg_header, ret
            else:
                return ret
        else:
                SyntaxError("invalid msg")
            

if __name__ == "__main__":
    connectmsg = 'CONNECT,START'
    obumsg = "OBU-DATA,OBU-INFO,21352436531,ISSUE-INFO,3252421"
    requsermsg = 'REQ_USER,user_idx,53d9d831-c300-11eb-bff3-0ad78b68558e'
    prodinfomsg = 'PROD-INFO,REQ,EEVEE'
    payinfomsgCARD = 'PAY-INFO,CARD,0000,465411,524500,47681,0123456,20230313,05,018'
    payinfomsgYPAY = 'PAY-INFO,YPAY'
    
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
    