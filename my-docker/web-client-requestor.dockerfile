FROM python:latest
COPY ./web-client /src
RUN pip install requests
CMD python /src/requestor.py
