from io import TextIOWrapper

from .entity import DataEntity, CmdDataEntity

import os
from os.path import exists
import platform
from pydantic import BaseModel
from typing import Optional, List
import re

class MsgModel(BaseModel):
    channel: Optional[str] = None
    username0: Optional[str] = None
    message0: Optional[str] = None
    username1: Optional[str] = None
    message1: Optional[str] = None

# 디렉토리 경로 ( os별 표현 수정 )
def check_the_system_os_type():
    PlatformOs = platform.platform()
    PlatformOs = PlatformOs.split('-')
    list = []
    if PlatformOs[0] == "Windows":
        list.append('option\\')
        list.append('shared_docs\\')
    else:
        list.append('option/')
        list.append('shared_docs/')
    return list


# 디렉토리 변수값으로 저장
dirPath = check_the_system_os_type()
print(dirPath[0], dirPath[1])
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, dirPath[0])
FILE_DIR = os.path.join(STATIC_DIR, dirPath[1])


def separate_string(rawdata: str) -> DataEntity:
    datasection_end = (int(rawdata[2:6],16)+8)
    print(datasection_end)
    rev_data = DataEntity(
        stx=rawdata[0:2],
        data_length=rawdata[2:6],
        direction=rawdata[6:8],
        data=rawdata[8:datasection_end],
        crc=rawdata[datasection_end+1:datasection_end+3],
        etx=rawdata[datasection_end+3:datasection_end+5]
    )

    return rev_data


def data_parsing(rawdata: str) -> list:
    parsing_data = rawdata.split(',')
    return parsing_data


async def file_exist_check(file_path: str):
    try:
        os.makedirs(FILE_DIR)
    except OSError:
        if not os.path.isdir(FILE_DIR):
            raise

    check_file = exists(file_path)
    # print(check_file)
    if check_file is False:
        f = open(file_path,'w')
        f.write("")
        f.close()
        check_file = exists(file_path)
    return check_file


async def file_read(fd: TextIOWrapper, r_data: MsgModel) -> MsgModel:
    r_data_list: List = []
    r_data_list = fd.readlines()
    rdata: MsgModel = r_data
    print(r_data_list)
    for i in r_data_list:
        if i.find("OBU_DATA") != -1:
            spd = i.strip()
            spd = spd.split(',')
            rdata.username0 = spd[0]
            rdata.message0 = spd[3]
            # r_data(username0=)
        elif i.find("USER_INFO") != -1:
            spd = i.strip()
            spd = spd.split(',')
            rdata.username1 = spd[0]
            rdata.message1 = spd[3]
        else:
            ...

    return rdata


async def file_write():
    ...


async def file_clear(ch: str):
    file_path = FILE_DIR + ch + '.txt'
    rv = await file_exist_check(file_path)
    if rv is True:
        try:
            print("test")
            fd = open(file_path,'w')
            fd.seek(0)
            fd.truncate(0)

        except:
            ...

        fd.close()
    else:
        return -1


async def write_shared_data(ch: str, wdata: str):
    file_path = FILE_DIR + ch + '.txt'
    w_data = MsgModel(channel=ch)
    rv = await file_exist_check(file_path)
    if rv is True:
        try:
            fd = open(file_path,'a+')
            fd.write(wdata)

            return 0
        except:
            ...
    else:
        return -1


async def read_shared_data(ch: str):
    file_path = FILE_DIR + ch + '.txt'
    r_data = MsgModel(channel=ch)
    rv = await file_exist_check(file_path)
    if rv is True:
        try:
            fd = open(file_path)
            r_data = await file_read(fd, r_data)

            return r_data
        except:
            ...
    else:
        return -1


async def send_to_destination():
    ...