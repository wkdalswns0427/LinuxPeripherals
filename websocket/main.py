import os


import asyncio

from broadcaster import Broadcast
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
# from starlette.websockets import WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import Optional, List
import json

import httpx
from fastapi.responses import ORJSONResponse
from parsing_module.receiveProtocol import recvAndroid2Core

from parsing_module.module import separate_string, data_parsing, file_exist_check, write_shared_data, file_clear, read_shared_data, MsgModel

app = FastAPI()
BROADCAST_URL = os.environ.get("BROADCAST_URL", "memory://")

URL = "http://localhost:5000/websocket/" #"http://192.168.12.222:8000/websocket/" #"http://localhost:5000/websocket/CONNECT"

broadcast = Broadcast(BROADCAST_URL)
CHANNEL = "BUFFER"
CHANNEL_TEST = "0103"

TEST_CMD = "CONNECT"
TEST_MESSAGE = {'param1': 'START','param2' : '32'}      #data1/data2/crc/direction

r_data: MsgModel = None

matching_destination = {'01' : "CU", '03': 'kiosk'}


async def request(client):
    params = {'key1': 'value1', 'key2': ['value2', 'value3']}
    response = await client.post(URL,params=TEST_MESSAGE)
    print(response.text)
    return response.text
#
#
# async def called_api(data):
#     async with httpx.AsyncClient() as client:
#         result = await client.post(URL, params=data)
#         print(result.status_code)


async def called_api(command: str, data: json, ch: str, username: str):
    print("command:",command)
    print("data:",data)
    if command is None:
        return None
    if data is None:
        return None
    result = await httpx.AsyncClient().post(URL+command+'/', data=data)
    print(result.url)
    print(result.request.content)
    print(result.status_code)
    print(result.json())
    event = MessageEvent(username=username, message=str(result.json()))
    await broadcast.publish(channel=ch, message=event.json())
    print("published")
    return result


class MessageEvent(BaseModel):
    username: str
    message: str


class ReqMsgModel(BaseModel):
    channel: Optional[str] = None
    username0: Optional[str] = None
    message0: Optional[str] = None
    username1: Optional[str] = None
    message1: Optional[str] = None

#
# async def receive_message(websocket: WebSocket, username: str, proc_port: int):
#     async with broadcast.subscribe(channel=CHANNEL) as subscriber:
#         async for event in subscriber:
#             message_event = MessageEvent.parse_raw(event.message)
#             # # Discard user's own messages
#             # if message_event.username != username:
#             #     print(message_event)
#             #     await websocket.send_json(message_event.dict())
#
#
# async def send_message(websocket: WebSocket, username: str, proc_port: int = None):
#     data = await websocket.receive_text()
#     event = MessageEvent(username=username, message=data)
#     # event = MessageEvent(username=username, message=data)
#     await broadcast.publish(channel=CHANNEL, message=event.json())
#     return CHANNEL


async def send_message_test(websocket: WebSocket, username: str, ch: str):
    data = await websocket.receive_text()
    print("username:",username, "send_message_test:",data)
    print(len(data))
    if len(data) != 0:
        ch_a = int(ch[0:2])
        ch_b = int(ch[2:4])
        spd = data.strip()
        spd = spd.split(',')
        print(spd)
        if int(username) == ch_a:
            event = str(ch_a) + "," + data + "\n"
        else:
            event = str(ch_b) + "," + data + "\n"
        await write_shared_data(ch, event)
        event = MessageEvent(username=username, message=data)
        await broadcast.publish(channel=ch, message=event.json())
    return ch


async def receive_message_test(websocket: WebSocket, username: str, ch: str):
    async with broadcast.subscribe(channel=ch) as subscriber:
        async for event in subscriber:
            command = None
            json_data = None
            event_dict = json.loads(event.message)
            sender_name = event_dict['username']
            sender_msg = event_dict['message']
            message_event = MessageEvent.parse_raw(event.message)
            print(username,':',message_event.message)
            if sender_name == username:
                command, json_data = await command_data_parser(message_event.message)
            if 'destination' in sender_msg:
                sender_msg = sender_msg.replace("\'","\"")
                sender_json = json.loads(sender_msg)

                await websocket.send_json(data=sender_json['contents'])
            rdata = await read_shared_data(ch)
            # print(username,"rcv:", rdata)
            print(username,":","parsing_Data:",command, json_data)
            print(username,":",event.message)
            return rdata, command, json_data

#
# async def call_apis(websocket: WebSocket):
#     async with broadcast.subscribe(channel=CHANNEL) as subscriber:
#         async for event in subscriber:
#             message_event = MessageEvent.parse_raw(event.message)
#             if message_event:
#                 async with httpx.AsyncClient() as client:
#                     response = await client.post(URL, params=TEST_MESSAGE)
#                     print("resp:", response.text)
#                     return response.text


async def command_data_parser(data: str):
    command: str = ""
    json_data: json = ""
    print("len:",len(data))
    if len(data) != 0:
        cuagent = recvAndroid2Core()
        command, json_data = await cuagent.protoDecoder(data)
    return command, json_data


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, username: str = "Anonymous", data: str = "" ):
    value = await websocket.accept()
    status_flag = 0
    task_return_value: list = None
    print(value)
    print("data:",data)
    print(websocket.client.port)
    web_port_num = int(websocket.client.port)
    # command, json_data = await command_data_parser(data)
    # print("command", command)
    # print("jsondata", json_data)
    try:
        while True :
            # call_api_task = asyncio.create_task(called_api(command, json_data))

            receive_message_task = asyncio.create_task(
                receive_message_test(websocket, username, CHANNEL_TEST)
            )
            send_message_task = asyncio.create_task(send_message_test(websocket, username, CHANNEL_TEST))

            done, pending = await asyncio.wait(
                { receive_message_task, send_message_task },
                return_when=asyncio.FIRST_COMPLETED,
                # asyncio.ALL_COMPLETED,asyncio.FIRST_COMPLETED
                )
            for task in pending:
                print("pending")
                task.cancel()
                status_flag = 1
                break
            for task in done:
                print(username,":done!!!")
                task_return_value = receive_message_task.result()
                print(username,":done data:",task.result())
                status_flag = 1
                break
            if status_flag == 1:
                print(username,":finish")
                return_values = await called_api(task_return_value[1], task_return_value[2],CHANNEL_TEST, username)
                if return_values is not None:
                    print(type(return_values))
                    print(return_values.json())
                # event = MessageEvent(username=username, message=return_values.text)
                # await broadcast.publish(channel=CHANNEL_TEST, message=event.json())
                # status_flag = 0
    except WebSocketDisconnect:
        await websocket.close()
        #client쪽에서 disconnect를 한 경우 websocket을 close 처리



@app.on_event("startup")
async def startup():
    await broadcast.connect()


@app.on_event("shutdown")
async def shutdown():
    await broadcast.disconnect()
