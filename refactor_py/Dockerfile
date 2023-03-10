FROM python:3.9

RUN mkdir /socket
WORKDIR /socket/

COPY ./src/ /socket/src/
COPY ./requirements.txt /socket/
COPY ./main.py /socket/

RUN pip3 install -r requirements.txt
EXPOSE 12242

CMD ["python3", "-u","/socket/main.py"]