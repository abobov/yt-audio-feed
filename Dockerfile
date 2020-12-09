FROM python:3

MAINTAINER Anton Bobov <anton@bobov.name>

WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && python -c 'from pypandoc.pandoc_download import download_pandoc; download_pandoc(version="2.10.1")'
COPY . .
ENTRYPOINT ["python", "./main.py"]
