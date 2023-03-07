# be aware of firewall when using socket
# ufw disable 
# or
# ufw enable \n ufw allow <port>

import socket
import datetime as dt
from src.commands import Commands
import src.aes128 as aes
from src.customcrc16 import CRC16_CCITTFALSE
import src.keyfile as keyfile
from src.utils import utils

encrypt_key = keyfile.str_encrypt_key
IV = keyfile.str_IV

SERVER_IP = '192.168.11.20'
SERVER_PORT = 12242
SIZE = 512
SERVER_ADDR = (SERVER_IP, SERVER_PORT)

def socketClientSetup():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(SERVER_ADDR)

    return client_socket


def socketRead(client_socket):
    crcagent = CRC16_CCITTFALSE()
    aesagent = aes.AES128Crypto(encrypt_key, IV)
    commands = Commands()
    util = utils()
    # client, addr = client_socket.accept()

    while True:
        content = client_socket.recv(SIZE)
        print("---------------------------------------------------------")
        print("read data : ", content, "type : ", type(content))
        print("read data list : ", list(content),  "type : ", type(list(content)[1]))

        if len(content) == 0:
            break
        
        # respond to kiosk access request 0x10
        elif content[3] == 0x10 and crcagent.crcVerifyXMODEM(content):
            commands.sendCORERESP(client_socket=client_socket, content=content)

        # check 0xE0 command ACK
        elif content[3] == 0xE0 and crcagent.crcVerifyXMODEM(content):
            # need to return ACK in 30ms
            ret = commands.sendACK(client_socket, content)
            print("SEND ACK : ", ret)

            SEQ = [content[1], content[2]]
            DATA = list(content[6:22]) 

            print("* * * * * * * * * * * * * * * * * * * * * * * *")
            decrypted_data = aesagent.decrypt(DATA, SEQ)
            info = decrypted_data[0:8]
            issue_info = decrypted_data[8:]
            info = util.list2str(list(info))
            issue_info = util.list2str(list(issue_info))
            print("dec_data : ",info)
            print("dec_data_issue_ : ",issue_info)
            print("* * * * * * * * * * * * * * * * * * * * * * * *")
            
            ret = util.postdata(info, issue_info)
            print("POST : ", ret)

        # check 0xE0 command NACK
        elif content[3] == 0xE0 and not crcagent.crcVerifyXMODEM(content):
            print("SEND NACK")
            commands.sendNACK(client_socket, content)
        
        elif content[3] == 0xE2 and crcagent.crcVerifyXMODEM(content):
            ########################################
            #####  React to INFO DEL REQUESTS  #####
            ########################################
            commands.sendACK(client_socket, content)
            pass
            
        else:
            SyntaxWarning("Invalid request") 
            pass

    print("Closing connection")
    client_socket.close()

def main():
    client_socket = socketClientSetup()
    socketRead(client_socket)
    

if __name__=="__main__":
    main()
