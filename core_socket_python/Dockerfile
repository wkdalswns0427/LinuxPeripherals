FROM python:3.9

RUN mkdir /socket/
WORKDIR /socket/

COPY ./run.sh /socket/
COPY ./Android_server/src/ /socket/Android_server/src/
COPY ./CU_client/src/ /socket/CU_client/src/
COPY ./Android_server/Android_server.py /socket/Android_server/Android_server.py
COPY ./CU_client/CU_client.py /socket/CU_client/CU_client.py
COPY ./requirements.txt /socket/
COPY ./obu_data.csv /socket/

RUN pip3 install -r requirements.txt
EXPOSE 5050

CMD ["./run.sh"]