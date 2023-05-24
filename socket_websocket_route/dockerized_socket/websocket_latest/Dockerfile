FROM python:3.9

RUN mkdir /ws_server/
WORKDIR /ws_server/

COPY ./modules/ /ws_server/modules/
COPY ./.idea/ /ws_server/.idea/
COPY ./config.ini/ /ws_server/config.ini
COPY ./data_class.py /ws_server/data_class.py
COPY ./message_broker.py /ws_server/message_broker.py
COPY ./websocket_logic.py /ws_server/websocket_logic.py
COPY ./main.py /ws_server/main.py
COPY ./requirements.txt /ws_server/

ENV PATH /home/$charmander/.local/bin:${PATH}

RUN pip3 install -r requirements.txt
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload", "--port", "8000"]
# CMD uvicorn main:app --host 0.0.0.0 --reload