FROM debian:latest

RUN apt update && apt upgrade -y
    git clone https://github.com/TioDexty/dexty && \
    pip install -r requirements.txt && \
CMD python main.py
