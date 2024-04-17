from dataclasses import dataclass

@dataclass
class readerComponents:
    STX:int = 0xBA
    ETX:int = 0XBB

    PAYMENT:int = 0x0A
    # RETURN:int = 0x0B
    REMAINING:int = 0x0C
    CHARGE:int = 0x0D
    ERR_WK:int = 0xE1
    ERR_WS:int = 0xE2