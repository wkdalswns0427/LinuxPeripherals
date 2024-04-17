from utils.commands import *


class DataFactory:
    def XOR_gate(self, data: list):
        fcc = data[0]
        for i in range(len(data) - 1):
            fcc = fcc ^ data[i + 1]
        return fcc

    def make_data(self, command, data: int):
        Dstr = str(data)
        if len(Dstr) > 6:
            while len(Dstr) > 6:
                Dstr = Dstr[:-2]
        elif len(Dstr) <= 4:
            while len(Dstr) < 6:
                Dstr = '0' + Dstr
        temp = []
        str_Dstr = str(Dstr)
        str_Dstr = str_Dstr.zfill(6)
        for i in range(3):
            index = i * 2
            tr_data = str_Dstr[index]+str_Dstr[index+1]
            temp.append(int(tr_data,16))
            # temp.append(int(Dstr[2 * i]) * 16 + int(Dstr[2 * i + 1]))
        data = [readerComponents.STX,readerComponents.STATUS_M2S, command, temp[0], temp[1], temp[2],readerComponents.ETX]
        return data

    def data_parser(self, reference,  data: list):
        print(f"data:{data}")
        reference[2] = 0x85
        try:
            print("in parser  ", data)
            for i in range(len(reference)):
                if reference[i] != data[i]:
                    return False
            return True
           

        except:
            with Exception as e:
                print(e)
