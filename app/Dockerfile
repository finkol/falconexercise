FROM python:3.6

ADD ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ADD . /app

# Run!
WORKDIR /app
CMD ["python", "sanic_app.py"]