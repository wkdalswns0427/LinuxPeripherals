# be aware of firewall when using socket
# ufw disable 
# or
# ufw enable \n ufw allow <port>

import socket
import datetime as dt
from src.commands import Commands
import src.aes128 as aes
from src.customcrc16 import CRC16_CCITTFALSE

SERVER_IP = 'serverip'
SERVER_PORT = 12242
SIZE = 128
SERVER_ADDR = (SERVER_IP, SERVER_PORT)

# def socketServerSetup():
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)     
#     server_socket.bind((ip_addr, port))
#     server_socket.listen(1)
#     return server_socket


def socketClientSetup():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(SERVER_ADDR)

    return client_socket



def socketRead(client_socket):
    crcagent = CRC16_CCITTFALSE()
    aesagent = aes.AES128Crypto()
    commands = Commands()
    # client, addr = server_socket.accept()

    while True:
        content = client_socket.recv(SIZE)
        print("data : ", content)

        if len(content) == 0:
            break
        
        # respond to kiosk access request 0x10
        elif content[3] == 0x10 and crcagent.crcVerifyXMODEM(content):
            commands.sendCORERESP(client_socket, content)

        # check 0x20 command ACK
        elif content[3] == 0x20 and crcagent.crcVerifyXMODEM(content):
            SEQ = [content[1], content[2]] # seq data according to datasheet
            ENCRYPTED_DATA = content[6:21]
            DECRYPTED_DATA = aesagent.decrypt(ENCRYPTED_DATA, SEQ)
            ########################################
            ####     DO SOMETHING WITH DATA     ####
            ########################################
            commands.sendACK(client_socket, content)

        # check 0x20 command NACK
        elif content[3] == 0x20 and not crcagent.crcVerifyXMODEM(content):
            commands.sendNACK(client_socket, content)

        else:
            print(content) 

    print("Closing connection")
    client_socket.close()

    
def main():
    client_socket = socketClientSetup()
    socketRead(client_socket)

if __name__=="__main__":
    main()
