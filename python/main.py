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

CU_IP = '192.168.11.20'
CU_PORT = 12242
SIZE = 512
CU_ADDR = (CU_IP, CU_PORT)

SERVER_IP = '192.168.11.127'
SERVER_PORT = 5050
SERVER_ADDR = (SERVER_IP, SERVER_PORT)

def socketClientSetup():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(CU_ADDR)
    return client_socket

def socketServerSetup():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(SERVER_ADDR)  # 주소 바인딩
    return server_socket




def socketRead(client_socket, server_socket):
    crcagent = CRC16_CCITTFALSE()
    aesagent = aes.AES128Crypto(encrypt_key, IV)
    commands = Commands()
    util = utils()
    # client, addr = client_socket.accept()
    server_socket.listen()
    android_socket, android_addr = server_socket.accept()

    while True:
        content = client_socket.recv(SIZE)
        print("---------------------------------------------------------")
        print(content)

        if len(content) == 0:
            break
        
        # respond to kiosk access request 0x10
        elif content[3] == 0x10 and crcagent.crcVerifyXMODEM(content):
            commands.sendCORERESP(client_socket, content)

        # check 0xE0 command ACK
        elif content[3] == 0xE0 and crcagent.crcVerifyXMODEM(content):
            # need to return ACK in 30ms
            ret = commands.sendACK(client_socket, content)
            print("SEND ACK : ", ret)

            SEQ = [content[1], content[2]]
            DATA = list(content[6:22])   # OBU 제조번호, 발행번호

            print("* * * * * * * * * * * * * * * * * * * * * * * *")
            decrypted_data = aesagent.decrypt(DATA, SEQ)
            info = util.list2str(list(decrypted_data[0:8]))
            issue = util.list2str(list(decrypted_data[8:]))
            print("dec_data_obu : ",info)
            print("dec_data_issue_ : ",issue)
            print("* * * * * * * * * * * * * * * * * * * * * * * *")
            
            ret = util.postOBUdata(info, issue)
            print("POST : ", ret)

            send_data = info + issue

            android_socket.sendall(bytes(send_data,encoding='utf-8'))


        # check 0xE0 command NACK
        elif content[3] == 0xE0 and not crcagent.crcVerifyXMODEM(content):
            print("SEND NACK")
            commands.sendNACK(client_socket, content)
        
        elif content[3] == 0xE2 and crcagent.crcVerifyXMODEM(content):
            commands.sendACK(client_socket, content)

        else:
            SyntaxWarning("Invalid request") 
            android_socket.close()
            pass

    print("Closing connection")
    client_socket.close()

def main():
    client_socket = socketClientSetup()
    server_socket = socketServerSetup()
    socketRead(client_socket, server_socket)
    

if __name__=="__main__":
    main()
