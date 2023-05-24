from typing import Optional, List
from dataclasses import dataclass

CU_IP : str = '192.168.0.20'
CU_PORT : int = 12242
SIZE : int = 512
CU_ADDR = (CU_IP, CU_PORT)

SERVER_IP : str = '192.168.0.10' # socket server : this odroid IP
SERVER_PORT : int = 5050
SERVER_ADDR = (SERVER_IP, SERVER_PORT)

CORE2AND = 0X23
AND2CORE = 0X32
header = [0x02, 0xff, 0xff, 0xff]
tail = [0xff,0xff, 0x03]
sequenceTimeout = 60*60*6 #in sec

# URLs
# amazon : ec2-13-125-239-250.ap-northeast-2.compute.amazonaws.com
dns_addr = "http://cloud.da-core.com/db-api/"
@dataclass
class URLs():
    websocket_url : str = f"ws://{SERVER_IP}:8000/ws?username=01"
    url_serachuserbyinput : str = f"{dns_addr}searchuserbyinput/"
    url_searchuserbyobu : str = f"{dns_addr}searchuserbyobu/"
    url_searchbypnum : str = f"{dns_addr}db-api/searchpnum/"
    db_api_url : str = f"{dns_addr}OBU_data_post"


@dataclass
class dataCode():
    # primary
    connect : str = "CONNECT"
    userinfo : str = "USER-INFO"
    requser : str = "REQ-USER"
    reqobu : str = "REQ-OBU"
    prodinfo : str = "PROD-OBU"
    payinfo : str = "PAY-INFO"
    prodresult : str = "PROD-RESULT"
    
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