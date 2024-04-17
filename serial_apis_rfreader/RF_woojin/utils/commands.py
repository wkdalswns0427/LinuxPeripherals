from dataclasses import dataclass

@dataclass
class readerComponents:
    STX:int = 0x02
    ETX:int = 0X03

    STATUS_M2S: int = 0x01
    STATUS_S2M: int = 0x00

    IS_CONNECTED: int = 0x80 #M2S ret echo
    WRITE_CARD: int = 0x81 #with amount to pay M2S ret echo
    TAG_AVAILABLE: int  = 0x82 #M2S ret echo

    ON_TAG: int = 0x83
    OFF_TAG: int = 0x84
    CHARGE_SUCCES: int = 0x85

# 0x02 STATUS COMMAND D1 D2 D3 0x03