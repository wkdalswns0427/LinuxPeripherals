from utils.imports import *
from utils.SerialAssets import SerialAgent
from utils.datafactory import DataFactory
from utils.commands import *
from utils.RFreader import RFreader

router = APIRouter()

class inquiryModel(BaseModel):

    class Config:
        orm_mode=True

class paymentModel(BaseModel):
    pay_amount: int

    class Config:
        orm_mode=True

class respModel(BaseModel):
    status : bool
    command: str
    pay_amount: int
    rem_amount: int

    class Config:
        orm_mode=True

@router.post("/rfpayment",response_model=respModel,status_code=status.HTTP_200_OK, description="rf payment input amount")
async def rfpayment(item : paymentModel): #item: paymentModel
    rfserial = SerialAgent()
    rf = RFreader()
    cnt = 0
    pay, stat = 0, False
    remaining_amt = 0

    # while(cnt < 3):
    #     # print(f"item.pay_amount:{item.pay_amount}")
    #     rf.send_command(readerComponents.REMAINING, item.pay_amount)
    #     stat, command, charge_amt, remaining_amt = await rf.read_response(1024)
    #     if stat:
    #         break
    #     cnt += 1
    #     if cnt == 5:
    #         rf.send_command(readerComponents.REMAINING, 0)

    # if item.pay_amount > remaining_amt:
    #     ret = respModel(
    #         status=False,
    #         command='',
    #         pay_amount=item.pay_amount,
    #         rem_amount=remaining_amt
    #     )
    #     return ret

    # cnt = 0
    while(cnt < 3):
        # print(f"item.pay_amount:{item.pay_amount}")
        rf.send_command(readerComponents.PAYMENT, item.pay_amount)
        stat, command, charge_amt, remaining_amt = await rf.read_response(1024)
        if stat:
            break
        cnt += 1
        if cnt==5:
            rf.send_command(readerComponents.CHARGE, 0)

    rfserial._close_port(rfserial.rfagent)
    if command in ["LOWBALANCE", "ERROR1", "ERROR2"]:
        ret = respModel(
            status = False,
            command=command,
            pay_amount=item.pay_amount,
            rem_amount=remaining_amt
        )
    else:
        ret = respModel(
            status = stat,
            command=command,
            pay_amount=item.pay_amount,
            rem_amount=remaining_amt
        )
    return ret

@router.post("/rfcharge",response_model=respModel,status_code=status.HTTP_200_OK, description="rf charge input amount")
async def rfpayment(item : paymentModel): #item: paymentModel
    rfserial = SerialAgent()
    rf = RFreader()
    cnt = 0
    pay, stat = 0, False

    while(cnt < 5):
        rf.send_command(readerComponents.CHARGE, item.pay_amount)
        stat, command, charge_amt, remaining_amt = await rf.read_response(1024)
        if stat:
            break
        cnt += 1
        if cnt==5:
            rf.send_command(readerComponents.CHARGE, 0)

    rfserial._close_port(rfserial.rfagent)

    ret = respModel(
        status = stat,
        command=command,
        pay_amount=charge_amt,
        rem_amount=remaining_amt
    )
    return ret

@router.post("/rfinquiry",response_model=respModel,status_code=status.HTTP_200_OK, description="rf card remaining amount")
async def rfpayment(): #item: paymentModel
    rfserial = SerialAgent()
    rf = RFreader()
    cnt = 0
    stat = False

    while(cnt < 5):
        rf.send_command(readerComponents.REMAINING, 0)
        stat, command, charge_amt, remaining_amt = await rf.read_response(1024)
        if stat:
            break
        cnt += 1
        if cnt==5:
            rf.send_command(readerComponents.REMAINING, 0)

    rfserial._close_port(rfserial.rfagent)

    ret = respModel(
        status = stat,
        command=command,
        pay_amount=charge_amt,
        rem_amount=remaining_amt
    )
    return ret