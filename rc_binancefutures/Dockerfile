FROM ubuntu:latest
RUN apt-get update && apt-get install -y python3 python3-pip cron libpq-dev python-dev supervisor git
COPY ./requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
RUN git clone https://github.com/Binance-docs/Binance_Futures_python.git apibinance && cd apibinance && python3 setup.py install 
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["/usr/bin/supervisord"]