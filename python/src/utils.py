import datetime as dt
import requests
from src.keyfile import db_url

class utils:
    def __init__(self):
        self.i = 10

    def get_YYYYMMddhhmmss(self):
        x = dt.datetime.now()
        x_format = x.strftime("%Y%m%d%H%M%S")
        return x_format
    

    def hexifyList(self, list):
        length = len(list)
        hexlist = []
        for i in range(length):
            hexlist.append(hex(list[i]))
        return hexlist


    def makeDateList(self, list):
        date = self.get_YYYYMMddhhmmss()
        length = len(date)
        for i in range(int(length/2)):
            date_component = date[2*i:2*i+2]      
            list[i+6] = int(date_component)
        

    def makeBCD(self):
        date = self.get_YYYYMMddhhmmss()
        length = len(date)
        BCD = []
        for i in range(int(length/2)):
            date_binary = date[2*i:2*i+2]
            date_bin1 = int(date_binary[0]); date_bin2 = int(date_binary[1])
            date_to_append = date_bin1<<4 | date_bin2
            BCD.append(date_to_append)
        return BCD
    
    def postOBUdata(self, obu_info, issue_info):
        x = dt.datetime.now()
        cur_dt = x.strftime("%Y-%m-%d %H:%M")
        header = {'Content-Type':'application/json; charset=utf-8'}
        
        datas = {
            'id' : self.i,
            'time' : cur_dt,
            'obu_info' : obu_info,
            'issue_info' : issue_info
        }

        response = requests.post(db_url, json=datas, headers=header)
        self.i += 1
        return response 
    
    # used at aes128
    def hexlist2str(self, list):
        L = len(list)
        str_list = []
        for i in range(L):
            hexstr = str(hex(list[i])).replace('0x','',1)
            str_list.append(hexstr)
        joined_list = r"\x" + r"\x".join(str_list)
        return joined_list
    

    def list2str(self, list):
        L = len(list)
        str_list = []
        for i in range(L):
            hexstr = hex(list[i]).replace('0x','')
            if len(hexstr) == 1:
                hexstr = "0"+hexstr
            str_list.append(hexstr)
        joined_list = ''.join(str_list)
        return joined_list
    
