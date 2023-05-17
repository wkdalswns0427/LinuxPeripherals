# be aware of firewall when using socket
# ufw disable 
# or
# ufw enable \n ufw allow <port>
import socket
import asyncio
import websockets
import time

from auth.auth import Auth
from src.commands import Commands
import src.aes128 as aes
from src.customcrc16 import CRC16_CCITTFALSE
import src.keyfile as keyfile
from src.utils import utils
from src.config import CU_ADDR, SIZE, URLs, sequenceTimeout
from interruptingcow import timeout

encrypt_key = keyfile.str_encrypt_key
IV = keyfile.str_IV
auth_handler = Auth()


def serviceSetup():
    crcagent = CRC16_CCITTFALSE()
    aesagent = aes.AES128Crypto(encrypt_key, IV)
    commands = Commands()
    util = utils()
    return crcagent, aesagent, commands, util


async def websocketSendData(data):
    async with websockets.connect(URLs.websocket_url) as wsc:
        await wsc.send(data)
    return data


def socketClientSetup():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(CU_ADDR)
    return client_socket


def E0action(content, aesagent):
    SEQ = [content[1], content[2]]
    OBU_DATA = list(content[6:22])   # OBU 제조번호, 발행번호

    decrypted_data = aesagent.decrypt(OBU_DATA, SEQ)
    print("obu_info : ",list(decrypted_data[0:8]))
    print("issue_info : ",list(decrypted_data[8:]))
    re_enc_obu = str(aesagent.re_encrypt(decrypted_data[0:8]))
    re_enc_issue = str(aesagent.re_encrypt(decrypted_data[8:]))

    # ws_data_str : str= 'OBU_DATA'+','+'obu_info'+','+re_enc_obu+','+'issue_info'+','+ re_enc_issue
    
    ws_data = {"sender" : "01",
               "destination" : "ypass-service-api",
               "contents" :{
                   "obu-info" : re_enc_obu,
                    "issue-info" : re_enc_issue
                    }
               }
    print("ws data : ", ws_data)
    try:
        asyncio.get_event_loop().run_until_complete(websocketSendData(ws_data))
    except:
        print("ws connection failed")
        pass


def E2action(content, aesagent,util):
    SEQ = [content[1], content[2]]
    OBU_DATA = list(content[6:22])   # OBU 제조번호, 발행번호

    decrypted_data = aesagent.decrypt(OBU_DATA, SEQ)
    obu_info = util.list2str(list(decrypted_data[0:8]))
    issue_info = util.list2str(list(decrypted_data[8:]))
    print("info del req obu : ",obu_info); print("info del req issue : ",issue_info)


def socketRead():
    cnt = 0
    crcagent, aesagent, commands, util = serviceSetup()
    client_socket = socketClientSetup()
    try:
        with timeout(sequenceTimeout, exception=RuntimeError):

            while True:
                cnt += 1
                content = client_socket.recv(SIZE)
                print(util.get_YYYYMMddhhmmss())
                print(content)

                if len(content) == 0:
                    break
                
                # respond to kiosk access request 0x10
                elif content[3] == 0x10 and crcagent.crcVerifyXMODEM(content):
                    commands.sendCORERESP(client_socket, content)

                # check 0xE0 command ACK
                elif content[3] == 0xE0 and crcagent.crcVerifyXMODEM(content):
                    # need to return ACK in 30ms
                    commands.sendACK(client_socket, content)
                    E0action(content,aesagent)

                    # must wait for 0xE2 msg
                    content = client_socket.recv(SIZE)
                    print(util.get_YYYYMMddhhmmss())
                    if content[3] == 0xE2 and crcagent.crcVerifyXMODEM(content):
                        commands.sendACK(client_socket, content)
                        E2action(content, aesagent,util)

                # check 0xE0 command NACK
                elif content[3] == 0xE0 and not crcagent.crcVerifyXMODEM(content):
                    print("SEND NACK")
                    commands.sendNACK(client_socket, content)
                
                elif content[3] == 0xE2 and crcagent.crcVerifyXMODEM(content):
                    commands.sendACK(client_socket, content)
                    E2action(content, aesagent,util)

                else:
                    SyntaxWarning("Invalid request") 
                    pass

    except RuntimeError:
        print("<< Closing connection at ", time.time(), " >>")
        client_socket.close()
        pass


def main():
    while True:
        socketRead()


if __name__=="__main__":
    
    main()