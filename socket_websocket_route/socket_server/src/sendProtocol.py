import time, requests,asyncio
from config import CORE2AND, header, tail,encode_config, dataCode, URLs
from customcrc16 import CRC16_CCITTFALSE
from utils import utils


class sendCore2Android():
    def __init__(self):
        self.util = utils()
        self.crcagent = CRC16_CCITTFALSE()

        self.previousOBU : str = ''
        self.lastSentTime : str = ''
    
    
    # data length 부분 제작 --> 2bytes HEX
    def makeLen(self, data : str):
        abs_length: int = hex(len(data))
        lenlen = len(abs_length)

        # format
        if lenlen <= 4:
            if len(abs_length) == 3:
                abs_length = abs_length[0:2] + "0" + abs_length[-1]
            len_h, len_l = 0, int(abs_length, 16)

        elif 4 < lenlen and lenlen <= 6:
            if len(abs_length) == 5:
                abs_length = abs_length[0:2] + "0" + abs_length[2:]
            len_h, len_l = int(abs_length[0:4], 16), int(abs_length[4:], 16)

        return len_h, len_l

    # data formatting function for all protocol logics
    def global_makeData(self, data : str):
        output : str = ''
        data = list(bytes(data, encoding=encode_config))
        localheader = header
        localheader[1], localheader[2] = self.makeLen(data); localheader[3] = CORE2AND
        crc_data = bytes( localheader + data + tail )
        crc_h, crc_l = self.crcagent.makeCRC(crc_data)
        tail[-3] = crc_h; tail[-2] = crc_l
        
        full_data = header + data + tail

        for d in full_data:
            output = output + str(d) + ","
        return bytes(output, encode_config)
    
    # data formatting function explicitly for OBU protocol logics
    # sample input : global_makeOBUData([1,"0000000115156004", "0000000000000000"], "RESP-OBU")
    # return : b'2,0,40,35,82,69,83,80,45,79,66,85,48,48,48,48,48,48,48,49,49,53,49,53,54,48,48,52,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,48,46,215,3,'
    def global_makeOBUData(self, data : str, prefix : str):
        output : str = ''; datastring : str = ''
        curtime = self.util.get_YYYYMMddhhmm()
        
        for i in range(data[0]):
            datastring = datastring + data[2*i+1]  + data[2*i+2]
        data = list(bytes(prefix + datastring, encoding=encode_config)) # obu data + issue data
        
        localheader = header
        localheader[1], localheader[2] = self.makeLen(data); localheader[3] = CORE2AND
        
        crc_data = bytes( localheader + data + tail )
        crc_h, crc_l = self.crcagent.makeCRC(crc_data)
        
        # 여기 로직은 아직 미정 
        if data != self.previousOBU:
            tail[-3] = crc_h; tail[-2] = crc_l
            full_data = localheader + data + tail
            
            for d in full_data:
                output = output + str(d) + ","
            self.lastSentTime = curtime; self.previousOBU = data
            
            return bytes(output, encode_config)
        
        elif data == self.previousOBU and curtime != self.lastSentTime:
            tail[-3] = crc_h; tail[-2] = crc_l
            full_data = localheader + data + tail

            for d in full_data:
                output = output + str(d) + ","
            self.lastSentTime = curtime; self.previousOBU = data
            
            return bytes(output, encode_config)
    
        else:
            return False
        
    # search user db based on obudata
    def searchUserDB_byOBU(self, obuinfo : str, issueinfo : str):
        response = requests.get(URLs.url_searchuserbyobu, params={"obu_info" : obuinfo, "issue_info" : issueinfo} )
        if response == None:
            # NOT-REGISTERD-OBU
            return None
        else :
            # user id 인 경우
            return response
       
        
    # search user db based on user input data --> parameters may change / uynspecified
    # this thing activates after <USER-INFO, NOT-REGISTERD-OBU> message
    def searchUserDB_byID(self, input_id : str,obuinfo : str, issueinfo : str):
        response = requests.get(URLs.url_serachuserbyinput, params={"user_input" : input_id,"obu_info" : obuinfo, "issue_info" : issueinfo} )
        if response == None:
            # 사용자 정보 없음
            return None
        else :
            # user id 인 경우
            return response
    
    
# --------------------------------------------------------------------------------------------------------------------
    # get these messages from WS
    def makeCONNECTData(self, msg : str):
        data  = msg + "," + dataCode.start
            
        localheader = header
        localheader[1], localheader[2] = self.makeLen(data); localheader[3] = CORE2AND
        crc_data = bytes( header + data + tail )
        crc_h, crc_l = self.crcagent.makeCRC(crc_data)
        tail[-3] = crc_h; tail[-2] = crc_l
                
        full_data = header + data + tail

        for d in full_data:
            self.output = self.output + str(d) + ","
        return bytes(self.output, 'utf-8')


    # check db api for user info
    # ret values may vary : NOT-REGISTERD-OBU, USER ID, NOT-REGISTERD-USER
    # this msg should be [True, obu num,issue num]  or [False], user_input data...]
    # input data should be made and given by general logic
    def makeUSERINFOData(self, msg : list):
        data = dataCode.userinfo + ','
        
        # obu 조회 먼저 해보는 케이스 
        if msg[0] == True: # default True( initial )
            # obu로 조회
            response = self.searchUserDB_byOBU(msg[1])
            # initial case : OBU 인식 - DB정보 없음
            if response == None :
                data += dataCode.nro # USER-INFO, NOT-REGISTERD-OBU
                # android proceeds to user input process if this msg is received
                ret = self.global_makeData(data)
                return ret 
            
            elif response != None:
                data += response # USER_INFO, "USER_ID"
                ret = self.global_makeData(data)
                return ret 
        
        # obu 조회 실패 케이스 
        # 외부에서 위 프로세스의 nro 데이터를 읽고 msg[0]을 False 화
        elif msg[0] == False:
            # input user data 로 조회 
            response = self.searchUserDB_byID(msg[1])
            if response == None :
                data += dataCode.nru # USER-INFO, NOT-REGISTERD-USER
                # android proceeds to user input process if this msg is received
                ret = self.global_makeData(data)
                return ret 
            
            elif response != None:
                data += dataCode.du + response # USER_INFO, DIFF-OBU, "USER_ID"
                ret = self.global_makeData(data)
                return ret 
    
    
    def makePRODINFOData(self, msg : list): # ["PROD-INFO", <product>]
        # fetch product info
        # dummy
        product_info = {"name" : "premium", "description":"aaaaaaaaaaaaaaaaaaaa"}
        
        # string-fy prod info
        data = msg + str(product_info) 
        ret = self.global_makeData(data)
        return ret
        
        
    def makeRESPOBUData(self, msg : list): # ["RESP-OBU", pnum]
        # check db with pnum
        data = ""
        response = requests.get(URLs.url_searchbypnum, params={"pnum" : msg[1]})
        if response.status_code == 200:
            num = len(response.json())
            for i in num:
                data = data + response.json()[i+1]
            prefix = msg[0] + num
        ret = self.global_makeOBUData(data, prefix)
        return ret
    
    
    def makeYPAYRESData(self):
        # check with YPAY API for result
        # dummy
        res = "success, 000001, 12000"
        data = dataCode.payinfo + dataCode.ypay + res
        ret = self.global_makeData(data)
        return ret
# --------------------------------------------------------------------------------------------------------------------
        
    
if __name__=="__main__":
    data = "CONNECT,START"
    
    sc = sendCore2Android()
    ret = sc.global_makeData(data)
    print(ret)
    
    data = [1,"0000000115156004", "0000000000000000"]
    ret = sc.global_makeOBUData(data, "RESP-OBU")
    print(ret)
    
    response = requests.get("http://localhost:8000/searchuserbyobu/", params={"obu_info" : "0000000115156004", "issue_info" : "0000000000000000"} )
    print(response)