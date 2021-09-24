# Computer vissions projects

## Installation
```commandline
pip install -r requirements.txt
```

## RUN from docker in Linux

```bash
docker run -it \
    -v /tmp/.X11-unix:/tmp/.X11-unix \ # mount the X11 socket
    -e DISPLAY=unix$DISPLAY \ # pass the display
    --device /dev/snd \ # sound
    --name computervision \
    --net=host
    ugwuanyi/computervision
```