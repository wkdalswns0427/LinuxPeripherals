import datetime as dt
import requests

class utils:

    def get_YYYYMMddhhmmss(self):
        x = dt.datetime.now()
        x_format = x.strftime("%Y%m%d%H%M%S")
        return x_format

    def hexlist2str(self, list):
        L = len(list)
        str_list = []
        for i in range(L):
            hexstr = str(hex(list[i])).replace('0x','',1)
            str_list.append(hexstr)
        joined_list = r"\x" + r"\x".join(str_list)
        joined_list = bytes(joined_list, encoding='utf-8')

        return joined_list
    
    def list2str_encode(self, list):
        L = len(list)
        str_list = []
        for i in range(L):
            hexstr = hex(list[i]).replace('0x','',1)
            str_list.append(hexstr)
        joined_list = r"\x" + "".join(str_list)
        joined_list = bytes(joined_list, encoding='utf-8')

        return joined_list
    
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
    
    def postOBUdata(obu_info, issue_info):
        db_url = 'http://127.0.0.1:8000/{dir}'
        headers = {'Content-Type':'application/json; charset=utf-8'}

        datas = {
            'id' : 1,
            'obu_info' : obu_info,
            'issue_info' : issue_info
        }

        response = requests.post(db_url, data=datas, headers=headers)
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
    

    def list2str_encode(self, list):
        L = len(list)
        str_list = []
        for i in range(L):
            hexstr = hex(list[i]).replace('0x','',1)
            str_list.append(hexstr)
        joined_list = r"\x" + r"\x".join(str_list)
        joined_list.encode("ascii")
        return joined_list