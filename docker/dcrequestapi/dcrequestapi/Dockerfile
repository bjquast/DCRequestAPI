FROM ubuntu:22.04

WORKDIR /usr/src/app

RUN apt-get update --fix-missing
# && apt-get upgrade -y

RUN ln -fs /usr/share/zoneinfo/Europe/Berlin /etc/localtime \
  && DEBIAN_FRONTEND=noninteractive && apt-get install -y \
  apt-utils \
  software-properties-common python3-dev \
  python3-setuptools \
  python3-pip \
  unixodbc unixodbc-dev \
  tdsodbc \
  mysql-client \
  git \
  locales \
  language-pack-en-base \
  language-pack-de-base


RUN git clone -b main --single-branch https://github.com/bjquast/DCRequestAPI.git DCRequestAPI && \
  cd DCRequestAPI && \
  python3 setup.py develop

COPY set_config.py ./DCRequestAPI/set_config.py

ENTRYPOINT cd ./DCRequestAPI && python3 set_config.py config.ini.template config.ini && python3 set_config.py production.ini.template production.ini && pserve production.ini

CMD /usr/bin/bash

EXPOSE $PYRAMID_PORT
