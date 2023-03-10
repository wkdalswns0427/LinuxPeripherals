
from src.customcrc16 import CRC16_CCITTFALSE
from src.utils import utils
# Things I Send
# 0xff on variables
CORE2CU_ACK = [0x02, 0xff, 0xff, 0xA0, 0x00, 0x00, 0xff, 0xff, 0x03]
CORE2CU_NACK = [0x02, 0xff, 0xff, 0xA1, 0x00, 0x00, 0x00, 0x00, 0x03]
CORE2CU_RESP = [0x02, 0xff, 0xff, 0x11, 0x00, 0x07, 
                0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
                0xff, 0xff, 0x03]
CORE2CU_ANTENNA= [0x02, 0xff, 0xff, 0x50, 0x00, 0x01, 0xff, 0xff, 0xff, 0x03]

# Things I Read
CORE_ACCESS_REQ = [0x02, 0xff, 0xff, 0x10, 0x00, 0x00, 0xff, 0xff, 0x03]
OBU_INFO = [0x02, 0xff, 0xff, 0xE0, 0x00, 0x08,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0x03]
OBU_DELETE_REQ =  [0x02, 0xff, 0xff, 0xE2, 0x00, 0x08,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0x03]


class Commands:
    
    def __init__(self):
        self.crcagent = CRC16_CCITTFALSE()
        self.utils = utils()


    def sendACK(self, client_socket, content):
        CORE2CU_ACK[1] = content[1]
        CORE2CU_ACK[2] = content[2]

        crc_h, crc_l = self.crcagent.makeCRCXMODEM(bytes(CORE2CU_ACK))
        CORE2CU_ACK[-3] = crc_h; CORE2CU_ACK[-2] = crc_l

        client_socket.send(bytes(CORE2CU_ACK))
        return CORE2CU_ACK



    def sendNACK(self, client_socket, content):
        CORE2CU_NACK[1] = content[1]
        CORE2CU_NACK[2] = content[2]

        crc_h, crc_l = self.crcagent.makeCRCXMODEM(bytes(CORE2CU_NACK))
        CORE2CU_NACK[-3] = crc_h; CORE2CU_NACK[-2] = crc_l

        client_socket.send(bytes(CORE2CU_NACK))
        return CORE2CU_NACK
        
    def sendAntennaControl(self, client_socket, content, state):
        CORE2CU_ANTENNA[1] = content[1]
        CORE2CU_ANTENNA[2] = content[2]
        
        if state == 1:
            CORE2CU_ANTENNA[-4] = 0x01 # on
        elif state == 0:
            CORE2CU_ANTENNA[-4] = 0x00 # off
        

        crc_h, crc_l = self.crcagent.makeCRCXMODEM(bytes(CORE2CU_ANTENNA))
        CORE2CU_ANTENNA[-3] = crc_h; CORE2CU_ANTENNA[-2] = crc_l

        client_socket.send(bytes(CORE2CU_ANTENNA))


    def sendCORERESP(self, client_socket, content):
        CORE2CU_RESP[1] = content[1]
        CORE2CU_RESP[2] = content[2]

        bcdconvert = self.utils.makeBCD()
        for i in range(7):
            CORE2CU_RESP[i+6] = bcdconvert[i]

        crc_h, crc_l = self.crcagent.makeCRCXMODEM(bytes(CORE2CU_RESP))
        CORE2CU_RESP[-3] = crc_h; CORE2CU_RESP[-2] = crc_l
        encodedData = bytes(CORE2CU_RESP)

        client_socket.sendall(encodedData)
