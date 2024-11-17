FROM ubuntu:latest

WORKDIR /application
ARG PYTHON_VERSION

# COPY ./Python-3.9.0.tgz ./

RUN apt update && apt upgrade -y \
    && apt install -y python3-pip \
    && pip3 install wheel pylint pytest nbmake

RUN if [ "$PYTHON_VERSION" = "3.8" ] ; \
    then apt install -y python3.8 ; \
    else \
    apt install -y wget build-essential libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev libffi-dev uuid-dev \
    && wget https://www.python.org/ftp/python/3.9.0/Python-3.9.0.tgz \
    && tar xzf Python-3.9.0.tgz \
    && cd Python-3.9.0 \
    && ./configure \
    && make -j 4 \
    && make altinstall \
    && cd .. \
    && rm -rf Python-3.9.0.tgz \
    && rm -rf Python-3.9.0 \
    ; \
    fi

# RUN apt update && apt upgrade -y \
#     && apt install -y python3.8 \
#     && apt install -y build-essential libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev libffi-dev uuid-dev \
#     && tar xzf Python-3.9.0.tgz \
#     && cd Python-3.9.0 \
#     && ./configure \
#     && make -j 8 \
#     && cd .. \
#     && rm -rf Python-3.9.0.tgz \
#     && rm -rf Python-3.9.0 \
#     && apt install -y python3-pip \
#     && pip3 install wheel pylint pytest nbmake

