FROM python:3.9

WORKDIR /app/
EXPOSE 6677

COPY ./app.py /app/
COPY ./utils/ /app/utils/
COPY ./router/ /app/router/
COPY ./requirements.txt /app/

RUN pip3 install -r requirements.txt

CMD uvicorn app:app --host=0.0.0.0 --reload --port=6677
