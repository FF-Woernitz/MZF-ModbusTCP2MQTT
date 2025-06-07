FROM python:3-alpine

RUN apk add --no-cache py-pip

WORKDIR /opt/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python","-u", "./main.py"]