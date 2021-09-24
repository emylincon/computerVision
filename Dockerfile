FROM python:3.7

WORKDIR app

COPY . .

RUN apt update -y && apt install cmake -y && pip install -r requirements.txt

CMD ['bash']