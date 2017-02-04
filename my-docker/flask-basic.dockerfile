FROM python:latest
COPY ./flask-basic /src
RUN pip install -r /src/requirements.txt
CMD python /src/server.py
