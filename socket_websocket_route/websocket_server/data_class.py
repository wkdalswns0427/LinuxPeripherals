from pydantic import BaseModel
from typing import Optional, List

class WsDataBaseForm(BaseModel):
    sender: Optional[str]
    destination: Optional[str]
    contents: Optional[str]

class MessageEvent(BaseModel):
    username: Optional[str]
    message: Optional[str]

class ApiContents(BaseModel):
    method: str
    uri: Optional[str]
    param: Optional[str]