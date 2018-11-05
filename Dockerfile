FROM alpine

RUN echo "ipv6" >> /etc/modules

RUN apk --no-cache add build-base python3-dev py3-pip py3-psycopg2 jpeg-dev zlib-dev postgresql-dev 

ENV LIBRARY_PATH=/lib:/usr/lib

RUN mkdir /app

ADD app /app

WORKDIR /app

RUN pip3 install --upgrade pip
RUN ls /usr/bin | grep python
RUN pip3 install -r requirements.txt
