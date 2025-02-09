FROM python:3.12.7

WORKDIR /data

COPY ./main.py /data/main.py
COPY ./config.py /data/config.py
COPY ./taiga_api.py /data/taiga_api.py
COPY ./data_handler.py /data/data_handler.py
COPY ./requirements.txt /data/requirements.txt

RUN pip install -r /data/requirements.txt

CMD ["python", "./main.py", "--host", "0.0.0.0", "--port", "5001"]