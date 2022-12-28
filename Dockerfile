FROM ubuntu:22.10
RUN apt update
RUN apt install -y git zsh make
COPY ./Makefile /root/Makefile
