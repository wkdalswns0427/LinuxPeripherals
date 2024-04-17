from utils.imports import *
from utils.SerialAssets import SerialAgent
from utils.datafactory import DataFactory
from utils.commands import *
from utils.RFreader import RFreader

router = APIRouter()

class checkModel(BaseModel):
    status : bool
    remnant : int = 0
    class Config:
        orm_mode=True

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

@router.get("/connectionCheck",response_model=checkModel,status_code=status.HTTP_200_OK, description="check reader connection")
async def rfpayment(): #item: paymentModel
    rfserial = SerialAgent()
    rf = RFreader()
    data = rf.send_command(readerComponents.IS_CONNECTED,0)
    status = await rf.read_status_response(data, 1024)

    ret = checkModel(
        status=status
    )
    return ret

@router.post("/rfcharge",response_model=checkModel,status_code=status.HTTP_200_OK, description="rf payment input amount")
async def rfpayment(item : paymentModel): #item: paymentModel
    rfserial = SerialAgent()
    rf = RFreader()
    stat, cnt = False, 0


    cnt = 0
    while(cnt < 5):
        # print(f"item.pay_amount:{item.pay_amount}")
        data =rf.send_command(readerComponents.WRITE_CARD, item.pay_amount)
        stat = await rf.read_response(data,1024)
        if stat:
            break
        cnt += 1
        if cnt==5:
            rf.send_command(readerComponents.WRITE_CARD, 0)
    rf.send_command(readerComponents.CHARGE_SUCCES, item.pay_amount)

    rfserial._close_port(rfserial.rfagent)

    ret = checkModel(
        status=stat
    )
    return ret

@router.get("/rfinquiry",response_model=checkModel,status_code=status.HTTP_200_OK, description="rf card remaining amount")
async def rfpayment(): #item: paymentModel
    rfserial = SerialAgent()
    rf = RFreader()
    cnt = 0
    stat = False

    data = DataFactory.make_data(DataFactory, readerComponents.ON_TAG, 0)
    stat, rem = await rf.read_tag_response(data,1024)
    rf.send_command(readerComponents.ON_TAG, 0)


    rfserial._close_port(rfserial.rfagent)

    ret = checkModel(
        status=stat,
        remnant=rem
    )
    return ret