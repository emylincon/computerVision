FROM ubuntu

WORKDIR app

COPY . .

RUN apt update -y && apt install python3 python3-pip -y

RUN pip3 install -r requirements.txt

