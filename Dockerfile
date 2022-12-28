FROM ubuntu:22.10
RUN apt update
RUN apt install -y git zsh make iputils-ping
RUN cd && git clone https://github.com/at-github/.config.git
COPY ./Makefile /root/.config/Makefile
WORKDIR /root/.config
