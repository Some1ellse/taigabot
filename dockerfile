FROM python:3.12.7

WORKDIR /data

COPY ./main.py /data/main.py
COPY ./date_time.py /data/date_time.py
COPY ./requirements.txt /data/requirements.txt

RUN pip install -r /data/requirements.txt

CMD ["python", "./main.py", "--host", "0.0.0.0", "--port", "5000"]