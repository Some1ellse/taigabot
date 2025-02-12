FROM python:3.12.7

WORKDIR /data

RUN mkdir -p /data/handlers
RUN mkdir -p /data/config

COPY ./taiga_bot/main.py /data/main.py
COPY ./taiga_bot/config/__init__.py /data/config/__init__.py
COPY ./taiga_bot/config/config.py /data/config/config.py
COPY ./taiga_bot/handlers/data_handler.py /data/handlers/data_handler.py
COPY ./taiga_bot/handlers/taiga_api.py /data/handlers/taiga_api.py
COPY ./taiga_bot/handlers/taiga_api_auth.py /data/handlers/taiga_api_auth.py
COPY ./taiga_bot/handlers/__init__.py /data/handlers/__init__.py
COPY ./taiga_bot/requirements.txt /data/requirements.txt

RUN pip install -r /data/requirements.txt

CMD ["python", "./main.py", "--host", "0.0.0.0", "--port", "5000"]