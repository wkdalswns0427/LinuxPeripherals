FROM python:3.9

WORKDIR /app/
EXPOSE 6677

COPY ./app.py /app/
COPY ./utils/commands.py /app/utils/
COPY ./utils/datafactory.py /app/utils/
COPY ./utils/imports.py /app/utils/
COPY ./utils/RFreader.py /app/utils/
COPY ./utils/SerialAssets.py /app/utils/
COPY ./router/router_rf.py /app/router/
COPY ./requirements.txt /app/

RUN pip3 install -r requirements.txt

CMD uvicorn app:app --host=0.0.0.0 --reload --port=6677
