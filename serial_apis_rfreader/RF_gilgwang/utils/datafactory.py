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
        Dlist = [command, temp[0], temp[1], temp[2]]
        print(Dlist)
        fcc = self.XOR_gate(Dlist)
        data = [readerComponents.STX] + Dlist + [fcc, readerComponents.ETX]
        return data

    def data_parser(self, data: list):
        print(f"data:{data}")
        if data[0] != 0xCA:
            return "invalid value"
        try:
            if data[1] == 0x0C:
                command = "INQUIRY"
                # remaining amount
                remain_amt = data[6:9]
                remain_amt_str = []
                for component in remain_amt:
                    temp = str(component // 16) + str(component % 16)
                    if len(temp) < 2:
                        temp += "0"
                    print(temp)
                    remain_amt_str.append(temp)
                ramt = int(remain_amt_str[0] + remain_amt_str[1] + remain_amt_str[2])
                camt = 0
                return command, camt, ramt

            elif data[1] == 0x0D:
                command = "CHARGE"
                # charge amount
                charge_amt = data[3:6]
                charge_amt_str = []
                for component in charge_amt:
                    temp = str(component // 16) + str(component % 16)
                    if len(temp) < 2:
                        temp += "0"
                    charge_amt_str.append(temp)
                camt = int(charge_amt_str[0] + charge_amt_str[1] + charge_amt_str[2])
                # remaining amount
                remain_amt = data[6:9]
                remain_amt_str = []
                for component in remain_amt:
                    temp = str(component // 16) + str(component % 16)
                    if len(temp) < 2:
                        temp += "0"
                    remain_amt_str.append(temp)
                ramt = int(remain_amt_str[0] + remain_amt_str[1] + remain_amt_str[2])
                return command, camt, ramt

            elif data[1] == 0x0A:
                command = "PAYMENT"
                # charge amount
                pay_amt = data[3:6]
                pay_amt_str = []
                for component in pay_amt:
                    temp = str(component // 16) + str(component % 16)
                    if len(temp) < 2:
                        temp += "0"
                    pay_amt_str.append(temp)
                camt = int(pay_amt_str[0] + pay_amt_str[1] + pay_amt_str[2])
                # remaining amount
                remain_amt = data[6:9]
                remain_amt_str = []
                for component in remain_amt:
                    temp = str(component // 16) + str(component % 16)
                    if len(temp) < 2:
                        temp += "0"
                    remain_amt_str.append(temp)
                ramt = int(remain_amt_str[0] + remain_amt_str[1] + remain_amt_str[2])
                return command, camt, ramt

            elif data[1] == 0xE1:
                command = "ERROR1"
                # wrong card key
                camt, ramt = 0, 0
                return command, camt, ramt

            elif data[1] == 0xE2:
                command = "ERROR2"
                # wrong station
                camt, ramt = 0, 0
                return command, camt, ramt

            elif data[1] == 0xE3:
                command = "LOWBALANCE"
                # low balance
                camt, ramt = 0, 0
                return command, camt, ramt

        except:
            with Exception as e:
                print(e)
