FROM python:3.8-buster

RUN apt-get update && apt-get install -y \
    git \
    make \
    zip \
    poppler-utils

RUN git clone https://github.com/emareg/paper-checker.git /home/paper-checker

WORKDIR /home/paper-checker

RUN pip install -r requirements.txt
