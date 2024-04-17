from utils.imports import *
from utils.SerialAssets import SerialAgent
from utils.datafactory import DataFactory
from utils.commands import *
from utils.RFreader import RFreader

router = APIRouter()

class paymentModel(BaseModel):
    pay_amount: int
    
    class Config:
        orm_mode=True

class respModel(BaseModel):
    pay_amount: int
    status: bool

    class Config:
        orm_mode=True

@router.post("/rfpayment",response_model=respModel,status_code=status.HTTP_200_OK, description="rf payment input amount")
async def rfpayment(item : paymentModel): #item: paymentModel
    rfserial = SerialAgent()
    rf = RFreader()
    cnt = 0
    pay, stat = 0, False
    
    while(cnt < 5):
        rf.send_command(readerComponents.PAYMENT, item.pay_amount)
        pay, stat = await rf.read_response(1024)
        if stat:
            break
        cnt += 1
        if cnt==5:
            rf.send_command(readerComponents.PAYMENT, 0)

    rfserial._close_port(rfserial.rfagent)

    ret = respModel(
        pay_amount=pay,
        status=stat
    )
    return ret

