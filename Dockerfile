FROM ubuntu:focal

ARG GOLANG_VERSION=1.16.8
RUN apt-get update && apt-get install -y --no-install-recommends wget
RUN wget --no-check-certificate https://dl.google.com/go/go$GOLANG_VERSION.linux-amd64.tar.gz && tar -C /usr/local -xzf go$GOLANG_VERSION.linux-amd64.tar.gz

ENV CSS_EXTRA true
COPY . .

EXPOSE 8080

CMD [ "./", "8080" ]
