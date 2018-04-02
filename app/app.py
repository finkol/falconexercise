import os
import redis
from flask import Flask, request, Response
import uuid

app = Flask(__name__)

r = redis.StrictRedis(host=os.environ['REDIS_HOST'], port=6379, db=0)


@app.route("/json_dummy", methods=['PUT'])
def put_json():
    content = request.get_json()
    uuid_str = str(uuid.uuid4())
    r.set(uuid_str, content)
    bla = r.get(uuid_str)
    print(bla)
    return "Received"


@app.route('/')
def hello_world():
    return 'Hello World!!!'


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True)
