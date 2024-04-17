from utils.commands import *

class DataFactory:
    # def checksum(self,data):
    #     checksum = 0
    #     for i in range(0, len(data)):
    #         checksum += data[i]
    #     checksum =~checksum
    #     checksum&=0xff
    #     return checksum
    
    def make_data(self, command, D : int):
        Dstr = str(D); Dstr = Dstr[:-1]
        if len(Dstr) > 4:
            while len(Dstr) > 4:
                Dstr = Dstr[:-2]
        elif len(Dstr) < 4:
            while len(Dstr) < 4:
                Dstr = '0' + Dstr
        Dlist = [16*int(Dstr[0])+int(Dstr[1]),16*int(Dstr[2])+int(Dstr[3])]

        # Bstr = str(B); Bstr = Bstr[:-1]
        # if len(Bstr) > 6:
        #     while len(Bstr) > 6:
        #         Bstr = Bstr[:-2]
        # elif len(Bstr) <= 4:
        #     while len(Bstr) < 6:
        #         Bstr = '0' + Bstr
        # Blist = [16*int(Bstr[0])+int(Bstr[1]),16*int(Bstr[2])+int(Bstr[3]),16*int(Bstr[4])+int(Bstr[5])]

        datamodel = [readerComponents.STX, command, 0x00, 0x00, Dlist[0],Dlist[1],0x00,readerComponents.ETX]
        return datamodel

