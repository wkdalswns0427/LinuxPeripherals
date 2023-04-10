FROM python:3.9

RUN mkdir /client/
WORKDIR /client/

COPY ./src/ /client/src/
COPY ./CU_client.py /client/CU_client.py
COPY ./auth/ /client/auth/
COPY ./requirements.txt /client/

RUN pip3 install -r requirements.txt
EXPOSE 5050 12242 43402

CMD ["python3", "-u", "CU_client.py"]