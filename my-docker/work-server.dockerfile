FROM python:latest
COPY ./work-server /src
RUN pip install -r /src/requirements.txt
CMD python -u /src/server.py
