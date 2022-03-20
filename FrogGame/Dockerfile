FROM python:3.7

WORKDIR app

COPY . .

RUN apt update -y && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends apt-utils && \
    apt install -y apt-utils \
    cmake \
    beep \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgirepository1.0-dev \
    && pip install -r requirements.txt \
    && pip install pygobject

CMD ["python3", "FrogGame.py"]