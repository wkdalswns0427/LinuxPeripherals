from data_class import WsDataBaseForm, MessageEvent, ApiContents
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import httpx
from httpx import Response, Request
import configparser
import logging

config = configparser.ConfigParser()
config_ret = config.read('config.ini')

Gateway_URL = ( config['API_GATEWAY_SETTING']['api_gateway_url']
                          if config_ret is not None else "http://127.0.0.1:8888")


# config file read and apply
if 'DEBUG_SETTING' in config.sections():
    if 'http_debugging' in config['DEBUG_SETTING']:
        http_debugging: bool = ( config['DEBUG_SETTING']['http_debugging'] in ['True', 'true', 'TRUE', 'T'])
    else:
        http_debugging: bool = False

if http_debugging is True:
    logging.basicConfig(
        format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG
    )


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
        print(type(message_dict['contents']))
        data = str(message_dict['contents'])
        data = data.replace('True', 'true')         #JSON format에서는 boolean type은 소문자로 표기
        data = data.replace('False', 'false')       #JSON format에서는 boolean type은 소문자로 표기
        ret_data: WsDataBaseForm = WsDataBaseForm(sender=message_dict['sender'],
                                                  destination=message_dict['destination'],
                                                  contents=data)
    except Exception as e:
        print(f"occurred error.{e}")
        raise WebSocketDisconnect
        return None

    return ret_data

async def parsing_api_contents(contents: str):
    method_val = ''
    uri_val = ''
    param_val = ''
    contents = contents.replace('\'', '\"')
    contents = contents.replace('\\', '')

    contents_dict = json.loads(contents)

    if 'method' in contents_dict:
        method_val = contents_dict['method']
        if 'uri' in contents_dict:
            uri_val = contents_dict['uri']
        if 'header' in contents_dict:
            header_val = contents_dict['header']
        if 'param' in contents_dict:
            param_val = contents_dict['param']
        if 'data' in contents_dict:
            data_val = contents_dict['data']
        api_contents = ApiContents(method=method_val,
                                   uri=uri_val,
                                   header=header_val,
                                   param=param_val,
                                   data=data_val)
    else:
        api_contents = None

    return api_contents

async def get_api(api_contents: ApiContents) -> Response:
    result = await httpx.AsyncClient().get(Gateway_URL+'/'+api_contents.uri, params=api_contents.param, headers=api_contents.header)
    return result

async def post_api(api_contents: ApiContents) -> Response:
    data = json.dumps(api_contents.data)
    result = await httpx.AsyncClient().post(Gateway_URL + '/' + api_contents.uri, data=data, headers=api_contents.header)
    return result

async def put_api(api_contents: ApiContents) -> Response:
    data = json.dumps(api_contents.data)
    result = await httpx.AsyncClient().put(Gateway_URL + '/' + api_contents.uri, data=data, headers=api_contents.header)
    return result

async def del_api(api_contents: ApiContents) -> Response:
    result = await httpx.AsyncClient().delete(Gateway_URL + '/' + api_contents.uri, params=api_contents.param, headers=api_contents.header)
    return result


