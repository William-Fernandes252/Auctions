FROM python:3

# Install dependencies
COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r /usr/src/app/requirements.txt

# Set entrypoint
COPY compose/entrypoint.sh /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

# Set app inicialization script
COPY compose/start.sh /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

# Set celery worker inicialization script
COPY compose/celery/worker/start.sh /start-celery-worker
RUN sed -i 's/\r$//g' /start-celery-worker
RUN chmod +x /start-celery-worker

# Set celery beat inicialization script
COPY compose/celery/beat/start.sh /start-celery-beat
RUN sed -i 's/\r$//g' /start-celery-beat
RUN chmod +x /start-celery-beat

WORKDIR /usr/src/app

ENTRYPOINT ["/entrypoint"]