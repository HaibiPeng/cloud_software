FROM alpine:3.12

WORKDIR /usr/app
ENV VAR=10 \
    MSG="Hello Docker!"

COPY ./fibonacci.sh ./
COPY ./helloDocker.sh ./

RUN chmod +x fibonacci.sh

CMD ["sh", "./fibonacci.sh"]
