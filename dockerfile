FROM python:3.12.7

WORKDIR /data

RUN mkdir -p /data/Handlers

COPY ./main.py /data/main.py
COPY ./config.py /data/config.py
COPY ./Handlers/data_handler.py /data/Handlers/data_handler.py
COPY ./Handlers/taiga_api.py /data/Handlers/taiga_api.py
COPY ./Handlers/taiga_api_auth.py /data/Handlers/taiga_api_auth.py
COPY ./Handlers/__init__.py /data/Handlers/__init__.py
COPY ./requirements.txt /data/requirements.txt

RUN pip install -r /data/requirements.txt

CMD ["python", "./main.py", "--host", "0.0.0.0", "--port", "5000"]