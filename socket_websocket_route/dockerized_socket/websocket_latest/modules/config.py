from typing import Optional, List
from dataclasses import dataclass

SERVER_IP : str = '192.168.11.127'
SERVER_PORT : int = 5050
SERVER_ADDR = (SERVER_IP, SERVER_PORT)

CU2CORE = 0x12
CORE2AND = 0X23
AND2CORE = 0X32
header = [0x02, 0xff, 0xff, 0xff]
tail = [0xff,0xff, 0x03]

encode_config = 'utf-8'

# URLs
@dataclass
class URLs():
    websocket_url : str = "ws://127.0.0.1:8000/ws/andserver"
    url_serachuserbyinput : str = "http://localhost:8000/searchuserbyinput/"
    url_searchuserbyobu : str = "http://localhost:8000/searchuserbyobu/"
    url_searchbypnum : str = "http://localhost:8000/searchpnum/"


@dataclass
class dataCode():
    # primary
    connect : str = "CONNECT"
    userinfo : str = "USER_INFO"
    requser : str = "REQ_USER"
    reqobu : str = "REQ_OBU"
    prodinfo : str = "PROD_INFO"
    payinfo : str = "PAY_INFO"
    prodresult : str = "PROD_RESULT"
    obudata : str = "OBU_DATA" # 0x12 dir
    
    # secondary
    c_possible : str = "POSSIBLE"
    c_inproc : str = "IN-PROC"
    
    ru_pnum : str = "PNUM"
    ro_pnum : str = "PNUM"
    
    start : str = "START"
    ypay : str = "YPAY"
    
    nro : str = "NOT-REGISTERED-OBU"
    nru : str = "NOT-REGISTERED-USER"
    du : str = "DIFF-USER"
    
    # trinket
    date : str = "DATETIME" #YYYYMMDDHHmmss