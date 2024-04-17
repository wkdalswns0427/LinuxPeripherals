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

    async def read_response(self, size):
        status = True
        ret = self.rfserial.read(self.rfserial.rfagent, size,timeout=4)
        self.rfserial.rfagent.flush()
        ret = list(ret)
        print(ret)

        if len(ret) <= 7:
            return False, "", 0, 0
        
        echo = ret[0:7]
        if echo[0] != 0xCA:
            status = False
            ret = self.rfserial.read(self.rfserial.rfagent, size,timeout=4)
            self.rfserial.rfagent.flush()
            ret = list(ret)
            print(ret)
        resp = ret[7:]
        print(f"resp:{resp}")
        command, charge_amt, remaining_amt = self.dfac.data_parser(resp)
        status = True
        
        return status, command, charge_amt, remaining_amt