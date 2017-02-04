FROM python:latest
COPY ./misc /src
RUN pip install flask
CMD ["python", "/src/python-print.py"]
