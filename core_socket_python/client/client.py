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
from src.config import CU_ADDR, CU_IP, CU_PORT, SERVER_ADDR, SERVER_IP, SERVER_PORT, SIZE
from interruptingcow import timeout

encrypt_key = keyfile.str_encrypt_key
IV = keyfile.str_IV

def socketClientSetup():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(CU_ADDR)
    return client_socket

def socketRead():
    crcagent = CRC16_CCITTFALSE()
    aesagent = aes.AES128Crypto(encrypt_key, IV)
    commands = Commands()
    util = utils()
    client_socket = socketClientSetup()
    try:
        with timeout(60*5, exception=RuntimeError):
            while True:
                content = client_socket.recv(SIZE)
                print("* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *")

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

                    current_time = util.get_YYYYMMddhhmmss()

                    SEQ = [content[1], content[2]]
                    DATA = list(content[6:22]) 

                    decrypted_data = aesagent.decrypt(DATA, SEQ)
                    info = util.list2str(list(decrypted_data[0:8]))
                    issue_info = util.list2str(list(decrypted_data[8:]))
                    print("dec_data : ",info); print("dec_data_issue_ : ",issue_info)
                    # re-encryption for stablization
                    re_enc_obu = str(aesagent.re_encrypt(decrypted_data[0:8]))
                    re_enc_issue = str(aesagent.re_encrypt(decrypted_data[8:]))

                    ret = util.posTdata(info, issue_info)
                    print("POST : ", ret)

                    writedata = [util.get_YYYYMMddhhmmss(), info, issue_info]
                    util.write2csv("./data.csv", writedata)
                    
                    # must wait for 0xE2 msg
                    content = client_socket.recv(SIZE)
                    if content[3] == 0xE2 and crcagent.crcVerifyXMODEM(content):
                        commands.sendACK(client_socket, content)

                # check 0xE0 command NACK
                elif content[3] == 0xE0 and not crcagent.crcVerifyXMODEM(content):
                    print("SEND NACK")
                    commands.sendNACK(client_socket, content)

                elif content[3] == 0xE2 and crcagent.crcVerifyXMODEM(content):
                    commands.sendACK(client_socket, content)

                else:
                    SyntaxWarning("Invalid request") 
                    pass

    except RuntimeError:
        print("Closing connection")
        client_socket.close()
        pass

    
def main():
    while True:
        socketRead()
    

if __name__=="__main__":
    main()
