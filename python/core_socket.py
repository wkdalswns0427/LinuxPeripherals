# be aware of firewall when using socket
# ufw disable 
# or
# ufw enable \n ufw allow <port>

import socket
import datetime as dt
from commands import Commands
from crc16 import CRC16_CCITTFALSE

ip_addr = '0.0.0.0'
port = 5051

def socketSetup():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)     
    server_socket.bind((ip_addr, port))
    server_socket.listen(1)
    return server_socket


def get_YYYYMMddhhmmss():
    x = dt.datetime.now()
    x_format = x.strftime("%Y%m%d%H%M%S")
    return x_format


def socketRead(server_socket):
    crcagent = CRC16_CCITTFALSE()
    client, addr = server_socket.accept()

    while True:
        content = client.recv(32)
        # need to revert content to list data
        content = content.decode('utf-8')
        content = eval(content) # if original code was written in list -> str conversion
        print(content)

        if len(content) == 0:
            break
        
        # respond to kiosk access request 0x10
        elif content[3] == 0x10 and crcagent.crcVerify(content):
            date = get_YYYYMMddhhmmss()
            Commands.sendCORERESP(server_socket, addr, content, date)

        # check 0x20 command ACK
        elif content[3] == 0x20 and crcagent.crcVerify(content):
            OBU_DATA = content[6:21]   # OBU 제조번호
            ISSUE_DATA = content[6:21] # OBU 발급번호
            ########################################
            ##  DO SOMETHING WITH OBU&ISSUE DATA  ##
            ########################################
            Commands.sendACK(server_socket, addr, content)

        # check 0x20 command NACK
        elif content[3] == 0x20 and not crcagent.crcVerify(content):
            Commands.sendNACK(server_socket, addr, content)

        else:
            print(content) 

    print("Closing connection")
    client.close()


if __name__=="__main__":
    crcagent = CRC16_CCITTFALSE()
    print(crcagent.crcVerify([0x02, 0x00, 0x01, 0x10, 0x00, 0x00, 0x24, 0xdb, 0x03]))
    get_YYYYMMddhhmmss()
