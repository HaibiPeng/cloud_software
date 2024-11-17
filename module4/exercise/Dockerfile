FROM python:3.8.5-alpine3.12

WORKDIR /usr/app

RUN apk add gcc libc-dev linux-headers zlib-dev jpeg-dev libjpeg

COPY ./ ./
RUN pip install -r requirements.txt

EXPOSE 5000

#RUN export FLASK_APP=app && \
#    export FLASK_ENV=development && \
#    export FLASK_DEBUG=1

CMD ["flask", "run", "--host=0.0.0.0"]