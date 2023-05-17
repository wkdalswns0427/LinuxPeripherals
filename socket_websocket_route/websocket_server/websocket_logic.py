from data_class import WsDataBaseForm, MessageEvent, ApiContents
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import httpx
from httpx import Response, Request
import configparser

config = configparser.ConfigParser()
config_ret = config.read('config.ini')

Gateway_URL = ( config['API_GATEWAY_SETTING']['api_gateway_url']
                          if config_ret is not None else "http://127.0.0.1:8888")


async def check_destination(destination: str, username: str):
    # 목적지를 체크하는 함수
    if destination == username:
        print(f"{username}: call me!!")
        return True
    elif destination == "broadcast":
        # 모든 서비스에 notification을 전달해야 하는 경우. 예) alarm
        print(f"{username}: call all")
        return True
    else:
        return False

async def message_separation(event: MessageEvent):
    # 메세지를 분리'
    try:
        event_dict = json.loads(event.message)
        message_dict = json.loads(event_dict['message'])
        ret_data: WsDataBaseForm = WsDataBaseForm(sender=message_dict['sender'],
                                                  destination=message_dict['destination'],
                                                  contents=str(message_dict['contents']))
    except:
        print("occurred error.")
        raise WebSocketDisconnect
        return None

    return ret_data

async def parsing_api_contents(contents: str):
    method_val = ''
    uri_val = ''
    param_val = ''
    contents = contents.replace('\'', '\"')
    contents_dict = json.loads(contents)

    if 'method' in contents_dict:
        method_val = contents_dict['method']
        if 'uri' in contents_dict:
            uri_val = contents_dict['uri']
        if 'param' in contents_dict:
            param_val = contents_dict['param']
    api_contents = ApiContents(method=method_val,
                               uri=uri_val,
                               param=param_val)

    return api_contents

async def get_api(api_contents: ApiContents) -> Response:
    print(api_contents)
    print(Gateway_URL)
    result = await httpx.AsyncClient().get(Gateway_URL+'/'+api_contents.uri, params=api_contents.param)
    print(result)
    return result

async def post_api():
    ...

async def put_api():
    ...

async def del_api():
    ...


