import asyncio
import os
import sqlite3

import pendulum
import redis
from flask import Flask, request, Response
import uuid

app = Flask(__name__)

#r = redis.StrictRedis(host=os.environ['REDIS_HOST'], port=6379, db=0)
db_conn = sqlite3.connect('falcon.db', check_same_thread=False)
db_cursor = db_conn.cursor()


@app.before_first_request
def initialize_db():
    db_cursor.execute("DROP TABLE IF EXISTS DUMMY_JSON")
    db_cursor.execute("""CREATE TABLE DUMMY_JSON
                    (uuid TEXT, 
                    json_payload TEXT, 
                    timestamp_inserted_to_db INTEGER, 
                    timestamp_received INTEGER)""")
    db_conn.commit()
    db_cursor.execute("INSERT INTO DUMMY_JSON VALUES ('1', 'Bla', '1', '2')")
    db_cursor.execute("SELECT * FROM DUMMY_JSON")
    print(db_cursor.fetchone())


async def consumer(uuid, json_payload, timestap_received):
    print("blabla")
    print(uuid, json_payload, timestap_received)


@app.route("/json_dummy", methods=['PUT'])
def put_json():
    timestamp_received = pendulum.now()
    content = request.get_json()
    uuid_str = str(uuid.uuid4())
    #r.set(uuid_str, content)
    #bla = r.get(uuid_str)
    asyncio.ensure_future(consumer(uuid_str, content, timestamp_received))
    return "Received"


@app.route('/')
def hello_world():
    print("yolo")
    return 'Hello World!!!'


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True)
