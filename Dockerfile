FROM ubuntu:22.10
ENV TERM xterm-256color
RUN apt update
RUN apt install -y git zsh make iputils-ping curl
RUN cd && git clone https://github.com/at-github/.config.git
COPY ./Makefile /root/.config/Makefile
ENTRYPOINT [ "zsh" ]
WORKDIR /root/.config
