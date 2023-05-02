from dataclasses import dataclass, field
from pydantic import PositiveInt, BaseModel
from typing import Optional, List


# stx 2 (02h)
# data length 4 (0000~ffffh)
# direction 2 (00~ffh)
# data xxxx (??)
# CRC 2 (0000~ffffh)
# etx 2 (03f)


class LengthRange(PositiveInt):
    le = 0xffff


class DataLength(BaseModel):
    # byte
    stx_len: Optional[int] = 1
    data_length_len: Optional[int] = 2
    direction_len: Optional[int] = 1
    crc_len: Optional[int] = 2
    etc_len: Optional[int] = 1


@dataclass
class DataEntity:
    stx: str
    data_length: str
    direction: str
    data: str
    crc: str
    etx: str


@dataclass
class CmdDataEntity:
    command: str
    param: list
