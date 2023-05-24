import datetime as dt
# import requests
import csv

class utils:

    def get_YYYYMMddhhmmss(self):
        x = dt.datetime.now()
        x_format = x.strftime("%Y%m%d%H%M%S")
        return x_format
    
    def get_YYYYMMddhhmm(self):
        x = dt.datetime.now()
        x_format = x.strftime("%Y%m%d%H%M")
        return x_format
    
    
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
    
    
    
    
    def hexifyList(self, list):
        length = len(list)
        hexlist = []
        for i in range(length):
            hexlist.append(hex(list[i]))
        return hexlist

    
    # used at aes128
    def hexlist2str(self, list):
        L = len(list)
        str_list = []
        for i in range(L):
            hexstr = str(hex(list[i])).replace('0x','',1)
            str_list.append(hexstr)
        joined_list = r"\x" + r"\x".join(str_list)
        return joined_list
    
    
    def str2hexstr(self, string):
        L = len(string)-1
        intlist = []
        for i in range(0,L,2):
            intlist.append(int(string[i:i+2]))
        return intlist

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
    
    
    def write2csv(self, fd, content : list):
        with open(fd, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(content)
            
    
    def readFcsv(self, fd):
        with open(fd, 'r', encoding='utf-8',newline='') as file:
            reader = csv.reader(file)
            for line in reader:
                data = line

        file.close()
        return data
