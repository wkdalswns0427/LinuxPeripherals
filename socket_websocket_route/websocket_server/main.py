import websockets.exceptions
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import os
import asyncio

from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import httpx
from httpx import Response
from message_broker import MessageEvent, broadcast, send_message, receive_message
import json

from data_class import WsDataBaseForm
from websocket_logic import parsing_api_contents, get_api, post_api, put_api, del_api
# from common import config_init, parsing_config_section
import configparser

app = FastAPI()


config = configparser.ConfigParser()
config_read = config.read('config.ini')
api_list: list = config['API_GATEWAY_SETTING']['api_list'].replace(" ","").split(",")

async def select_channel_func(username: str) -> str:
    # username이 포함된 채널명을 반환, config 파일 내에서 검색.
    ret_channel = "yper_auto_car_wash"
    return ret_channel


async def called_api(data: WsDataBaseForm, ch: str, username: str):
    if data.destination is None:
        print("No destination selected.")
        return None
    elif data.destination == "broadcast":
        print("For Client.")
        print(f"{username}: data.contents - ", data.contents)
        return None

    if data.contents is None:
        print("Contents is empty.")
        return None

    api_contents = await parsing_api_contents(data.contents)
    print(f"{username} api_contents:", api_contents)
    result: Response = None
    # result = await httpx.AsyncClient().post(Gateway_URL+'/'+data.destination, data=data)
    api_contents.uri = data.destination + '/'+api_contents.uri
    try:
        if api_contents.method == 'put':
            ...
        elif api_contents.method == 'get':
            result = await get_api(api_contents)
        elif api_contents.method == 'post':
            ...
        else:
            ...
    except :
        print("please check connection.")
        return None
    print(username, " ", result)
    if result is None:
        print(f"{username}: we don't call api.")
        return None

    # if (result.status_code - 200) > 100 :
    #     print("error occurred!!")
    #     return result
    print(result.reason_phrase)
    if data.destination not in api_list:
        print("The service you requested does not exist in the list. Please check again.")
        result_str = "{\"status_code\":\"404\",{\"reason_phrase\":\"Not Found\"}"
    elif (result.status_code - 200) > 100 :
        result_str = "{{\"status_code\":\"{}\",\"reason_phrase\":\"{}\"}}".format(result.status_code,result.reason_phrase)
    else:
        result_json = result.json()
        result_str = json.dumps(result_json)
        print(type(result_str))
        print(result_str)
    api_ret: WsDataBaseForm = WsDataBaseForm(
        # sender=data.destination,
        sender='manager',
        destination=username,
        contents=result_str
    )
    print(f"{username} - api_ret:", api_ret)
    event = MessageEvent(username=username, message=api_ret.json())
    print(f"api ret {username}:", event)
    print(f"event json {username}:", event.json())
    str_event_json = event.json().replace('///"','/"')
    print(str_event_json)
    await broadcast.publish(channel=ch, message=str_event_json)

    return result


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, username: str = "Anonymous", data: str = ""):
    # client 인증 필요
    value = await websocket.accept()
    web_port_num = int(websocket.client.port)  # 실행되고 있는 process 번호 ( 내부 logging?? )
    print(web_port_num)
    status_flag = 0
    task_return_value: list = None
    select_channel = await select_channel_func(username)
    try:
        while True:
            receive_message_task = asyncio.create_task(
                receive_message(websocket, username, select_channel)
            )
            # send_message_task = asyncio.create_task(send_message(websocket, username, select_channel))

            done, pending = await asyncio.wait(
                {receive_message_task}, #, send_message_task
                return_when=asyncio.FIRST_COMPLETED,
                # asyncio.ALL_COMPLETED,asyncio.FIRST_COMPLETED
            )
            print("username : ", username, "channel : ", select_channel)
            for task in pending:
                # print("pending")
                task.cancel()
                # status_flag = 1
                break
            for task in done:
                print(username, ":done!!!")
                try:
                    task_return_value: WsDataBaseForm = receive_message_task.result()
                except:
                    print("error occurred!!!! but still going")
                    status_flag = 0
                    
                    break
                else:
                    # print(username,":done data:",task.result())
                    status_flag = 1
                    # break
            if status_flag == 1:
                status_flag = 0
                print(username, ":finish")
                try:
                    print(task_return_value, select_channel, username)
                except:
                    print("error occurred!!!!")

                return_values = await called_api(task_return_value, select_channel, username)
                if return_values is not None:
                    # print(f"{username} report : ", return_values.json())
                    await receive_message(websocket, username, select_channel)      # return data를 client로 전송
                # await receive_message(websocket, username, select_channel)

    except WebSocketDisconnect:
        await websocket.close()


@app.on_event("startup")
async def startup():
    await broadcast.connect()


@app.on_event("shutdown")
async def shutdown():
    await broadcast.disconnect()
