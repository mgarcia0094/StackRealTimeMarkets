FROM ubuntu:latest
RUN apt-get update && apt-get install -y python3 python3-pip cron libpq-dev python-dev
COPY ./requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
COPY ./binancefutures /etc/cron.d/binancefutures
RUN chmod 0644 /etc/cron.d/binancefutures && crontab /etc/cron.d/binancefutures
ENV PYTHONUNBUFFERED 1
CMD cron -f