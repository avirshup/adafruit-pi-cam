FROM debian:buster-slim

RUN apt-get update
RUN apt-get install -y \
    git \
    python3 \
    python3-pip \
    vim
