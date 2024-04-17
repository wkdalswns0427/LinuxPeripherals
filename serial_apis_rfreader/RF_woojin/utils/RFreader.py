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

    def send_command(self, command, D:int):
        self.data = self.dfac.make_data(command, D)
        bytedata = bytes(self.data)
        self.rfserial.write(self.rfserial.rfagent, bytedata)
        self.rfserial.rfagent.flush()
        return self.data

    async def read_response(self, data, size):
        data[1] = 0x00
        status = True
        ret = self.rfserial.read(self.rfserial.rfagent, size,timeout=4)
        self.rfserial.rfagent.flush()
        ret = list(ret)
        print(ret)

        if len(ret) <= 5:
            return False
        echo = ret[0:7]
        #echo verification
        for i in range(len(data)):
            if data[i] != echo[i]:
                return False


        resp = ret[7:14]
        print(f"resp:{resp}")
        status = self.dfac.data_parser(data, resp)
        
        return status

    # check connection status 0x80
    async def read_status_response(self, data, size):
        data[1] = 0x00
        status = True
        ret = self.rfserial.read(self.rfserial.rfagent, size,timeout=4)
        self.rfserial.rfagent.flush()
        ret = list(ret)[:7]
        print(data)
        print(ret)

        #echo verification
        for i in range(len(data)):
            if data[i] != ret[i]:
                return False

        return True
    
    # check TAG status 0x83,4
    async def read_tag_response(self, data, size):
        data[1] = 0x00
        status = True
        ret = self.rfserial.read(self.rfserial.rfagent, size,timeout=4)
        self.rfserial.rfagent.flush()
        ret = list(ret)[:7]

        #echo verification
        for i in range(3):
            if data[i] != ret[i]:
                return False, 0

        remnant = (str((ret[3]//16)) +str(ret[3]%16)) + (str((ret[4]//16)) + str(ret[4]%16)) + (str((ret[5]//16)) + str(ret[5]%16)) 

        return True, int(remnant)