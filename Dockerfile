FROM python:3.10-alpine

WORKDIR /usr/src/app

RUN touch /usr/src/app/cron.log
RUN echo "*/2 * * * * cd /usr/src/app/ && python3 src/main.py >> /usr/src/app/cron.log" >> /var/spool/cron/crontabs/root

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
COPY config.yml .

CMD crond -f -d 8