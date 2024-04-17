from utils.imports import *
from utils.SerialAssets import SerialAgent
from utils.datafactory import DataFactory
from utils.commands import *

class RFreader:
    def __init__(self) -> None:
        self.rfserial = SerialAgent()
        self.dfac = DataFactory()
        self.rfserial._open_port(self.rfserial.rfagent)
        print(self.rfserial.rfagent)

    def send_command(self, command, D):
        self.data = self.dfac.make_data(command, D)
        bytedata = bytes(self.data)
        self.rfserial.write(self.rfserial.rfagent, bytedata)
        self.rfserial.rfagent.flush()

    async def read_response(self, size):
        status = True
        ret = self.rfserial.read(self.rfserial.rfagent, size,timeout=4)
        self.rfserial.rfagent.flush()
        ret = list(ret)
        print(ret)
        if len(ret) < 9:
            status = False
            D1str = str(ret[4]//16)+str(ret[4]%16)
            D2str = str(ret[5]//16)+str(ret[5]%16)+"0"
            if len(D2str)==2:
                D2str = "0"+D2str
            payment = int(D1str+D2str)
            return payment, status

        else:
            ret_echo = ret[0:8]; ret_resp = ret[8:]
            D1str = str(ret_resp[4]//16)+str(ret_resp[4]%16)
            D2str = str(ret_resp[5]//16)+str(ret_resp[5]%16)+"0"
            if len(D2str)==2:
                D2str = "0"+D2str
            payment = int(D1str+D2str)

            return payment, status
        # return payment, remaining