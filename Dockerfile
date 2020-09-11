FROM python:3

MAINTAINER Anton Bobov <anton@bobov.name>

WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENTRYPOINT ["python", "./main.py"]
