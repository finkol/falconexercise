FROM python:3.6

ADD ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ADD . /application

# Run!
WORKDIR /
CMD ["python", "application/main.py"]