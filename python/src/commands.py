
from src.customcrc16 import CRC16_CCITTFALSE
from src.utils import utils
# Things I Send
# 0xff on variables
CORE2CU_ACK = [0x02, 0xff, 0xff, 0xA0, 0x00, 0x00, 0xff, 0xff, 0x03]
CORE2CU_NACK = [0x02, 0xff, 0xff, 0xA1, 0x00, 0x00, 0x00, 0x00, 0x03]
CORE2CU_RESP = [0x02, 0xff, 0xff, 0x11, 0x00, 0x07, 
                0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 
                0xff, 0xff, 0x03]

# Things I Read
CORE_ACCESS_REQ = [0x02, 0xff, 0xff, 0x10, 0x00, 0x00, 0xff, 0xff, 0x03]
OBU_INFO = [0x02, 0xff, 0xff, 0x20, 0x00, 0x08,
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

        CRC_ACK = self.crcagent.hexlist2str(CORE2CU_ACK)

        crc_h, crc_l = self.crcagent.makeCRCXMODEM(CRC_ACK)
        CORE2CU_ACK[-3] = crc_h
        CORE2CU_ACK[-2] = crc_l

        client_socket.send(bytes(CORE2CU_ACK))


    def sendNACK(self, client_socket, content):
        CORE2CU_NACK[1] = content[1]
        CORE2CU_NACK[2] = content[2]

        CRC_NACK = self.utils.hexlist2str(CORE2CU_NACK)

        crc_h, crc_l = self.crcagent.makeCRCXMODEM(CRC_NACK)
        CORE2CU_NACK[-3] = crc_h
        CORE2CU_NACK[-2] = crc_l

        client_socket.send(bytes(CORE2CU_NACK))
    

    def sendCORERESP(self, client_socket, content):
        CORE2CU_RESP[1] = content[1]
        CORE2CU_RESP[2] = content[2]

        # self.utils.makeDateList(CORE2CU_RESP, date)
        # CRC_RESP = self.utils.hexlist2str(CORE2CU_RESP)
        # crc_h, crc_l = self.crcagent.makeCRCXMODEM(CRC_RESP)
        # CORE2CU_RESP[-3] = crc_h; CORE2CU_RESP[-2] = crc_l
        # print("send data list : ",CORE2CU_RESP)
        # print("send data : ",bytes(CORE2CU_RESP)) 
        # client_socket.send(bytes(CORE2CU_RESP))

        bcdconvert = self.utils.makeBCD()
        for i in range(7):
            CORE2CU_RESP[i+6] = bcdconvert[i]

        print(CORE2CU_RESP)
        CRC_RESP = self.utils.hexlist2str(CORE2CU_RESP)
        crc_h, crc_l = self.crcagent.makeCRCXMODEM(CRC_RESP)
        CORE2CU_RESP[-3] = crc_h; CORE2CU_RESP[-2] = crc_l
        
        encoded_data = self.utils.list2str_encode(CORE2CU_RESP)
        print("send data list : ",CORE2CU_RESP)
        print("send data : ",encoded_data)   
        
        client_socket.send(encoded_data)