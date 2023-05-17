from pydantic import BaseModel
from fastapi import WebSocket
from broadcaster import Broadcast
import os
import json
from modules.receiveProtocol import recvAndroid2Core
from websocket_logic import message_separation, check_destination
from data_class import WsDataBaseForm, MessageEvent

BROADCAST_URL = os.environ.get("BROADCAST_URL", "memory://")
broadcast = Broadcast(BROADCAST_URL)


async def command_data_parser(data: str):
    command: str = ""
    json_data: json = ""
    # print("len:",len(data))
    if len(data) != 0:
        rcv_data = recvAndroid2Core()
        command, json_data = await rcv_data.protoDecoder(data)
    return command, json_data


async def send_message(websocket: WebSocket, username: str, ch: str):
    data = await websocket.receive_text()
    # print("username:",username, "message:",data)
    # print(len(data))
    if len(data) != 0:
        event = MessageEvent(username=username, message=data)
        await broadcast.publish(channel=ch, message=event.json())
    return ch


async def receive_message(websocket: WebSocket, username: str, ch: str):
    async with broadcast.subscribe(channel=ch) as subscriber:
        async for event in subscriber:
            print(" In broker | username : ", username, "channel : ", ch)
            rcv_data: WsDataBaseForm = await message_separation(event)
            to_me: bool = await check_destination(rcv_data.destination, username)
            if to_me is True:
                print(f"sent to sender.{username}")
                print(f"{username} contents : ", rcv_data.contents)
                # await websocket.send_json(data=rcv_data.contents)     # send_json()으로 전송 시 /가 문자열 앞에 붙음.
                await websocket.send_text(data=rcv_data.contents)
                rcv_data.destination = None
                rcv_data.sender = None
                rcv_data.contents = None
                return rcv_data
            elif rcv_data.sender != username:
                print("skip this action.")
                rcv_data.destination = None
                rcv_data.sender = None
                rcv_data.contents = None
                return rcv_data
            else:
                print(f"not to me.{username}")
                return rcv_data

