import csv
import socket, time
import datetime as dt
from src.customcrc16 import CRC16_CCITTFALSE
from src.utils import utils
from src.config import SERVER_ADDR,  SIZE

class SocketServer():
    def __init__(self):
        self.util = utils()
        self.crcagent = CRC16_CCITTFALSE()
        self.previousCRC = [0,0]
    
    def serverConnect(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(SERVER_ADDR) 
        self.server_socket.listen()
        self.android_socket, self.android_addr = self.server_socket.accept()

    def readData(self):
        data = self.util.readFcsv("./data.csv")
        prevtime = data[0]
        data = self.util.str2hexstr(data[1] + data[2])
        return data, prevtime

    def makeData(self):
        time.sleep(0.5)
        data, prevtime = self.readData()
        output = ''
        
        header = [0x02, 0x10, 0xA0]
        tail = [0xff,0xff, 0x03]
        crc_data = bytes( header + data + tail )
        crc_h, crc_l = self.crcagent.makeCRC(crc_data)

        if prevtime != self.lastSentTime:
            self.previousCRC[0], self.previousCRC[1] = crc_h, crc_l
            tail[-3] = crc_h; tail[-2] = crc_l
            
            full_data = header + data + tail

            for d in full_data:
                output = output + str(d) + "!"
            print(self.lastSentTime, "/", prevtime, " ... ",output)
            self.lastSentTime = prevtime
            return bytes(output, 'utf-8')
        else:
            return False
    
    def send2Android(self):
        
        senddata = self.makeData()
        if senddata != False:
            self.android_socket.sendall(senddata)
            print("data sent")


def main():
    socketServer = SocketServer()
    socketServer.serverConnect()
    while(True):
        socketServer.send2Android()

if __name__ == "__main__":
    main()
