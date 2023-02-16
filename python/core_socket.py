# be aware of firewall when using socket
# ufw disable 
# or
# ufw enable \n ufw allow <port>

import socket
from commands import Commands
from crc16 import CRC16

ip_addr = '0.0.0.0'
port = 5051

def socketSetup():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)     
    server_socket.bind((ip_addr, port))
    server_socket.listen(1)
    return server_socket

def crcVerify(content):
    crc16class = CRC16()
    l = len(content)
    crc_sample = content[1:l-4]

    calc_crc = crc16class.crc16(crc_sample)
    calc_crc_h = calc_crc & 0b11110000
    calc_crc_l = calc_crc & 0b00001111

    if calc_crc_h == content[-3] and calc_crc_l == content[-2]:
        return True
    else:
        return False


def socketRead(server_socket):
    client, addr = server_socket.accept()
    while True:
        content = client.recv(32)
        content = content.decode('utf-8')
        content = eval(content) # if original code was written in list -> str conversion
        print(content)

        if len(content) ==0:
            break
        elif content[3] == 0x20 and crcVerify(content):
            Commands.sendACK(server_socket, addr)
        elif content[3] == 0x20 and not crcVerify(content):
            Commands.sendNACK(server_socket, addr)
        else:
            print(content) 
    print("Closing connection")
    client.close()

if __name__=="__main__":

    server_socket = socketSetup()
    while True:
        socketRead(server_socket)

    