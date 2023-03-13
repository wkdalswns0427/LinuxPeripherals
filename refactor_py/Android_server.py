import csv
import socket
import datetime as dt
from src.commands import Commands
import src.aes128 as aes
from src.customcrc16 import CRC16_CCITTFALSE
import src.customcrc16 as crc
from src.utils import utils
from src.config import SERVER_ADDR, SERVER_IP, SERVER_PORT, SIZE

class YpassSocketServer():
    def __init__(self):
        self.util = utils()
        self.crcagent = CRC16_CCITTFALSE()
    
    def serverConnect(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(SERVER_ADDR)  # 주소 바인딩
        self.server_socket.listen()
        self.android_socket, self.android_addr = self.server_socket.accept()
    
    def makeData(self):
        data = self.util.readFcsv("./obu_data.csv")
        data = self.util.str2hexstr(data[1] + data[2])
        output = ''
        
        header = [0x02, 0x10, 0xA0]
        tail = [0xff,0xff, 0x03]
        crc_data = bytes( header + data + tail )
        crc_h, crc_l = self.crcagent.makeCRC(crc_data)

        if crc_h != self.previousCRC[0] and crc_l != self.previousCRC[1]:
            self.previousCRC[0], self.previousCRC[1] = crc_h, crc_l
            tail[-3] = crc_h; tail[-2] = crc_l
            
            full_data = header + data + tail

            for d in full_data:
                output = output + str(d) + "!"
            
            return bytes(output, 'utf-8')
        else:
            return False
    
    def send2Android(self):
        
        senddata = self.makeData()
        if senddata != False:
            self.android_socket.sendall(senddata)


def main():
    socketServer = YpassSocketServer()
    socketServer.serverConnect()
    while(True):
        socketServer.send2Android()

if __name__ == "__main__":
    main()
