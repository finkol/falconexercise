from sanic import Sanic
import asyncio
import os
import sqlite3

import pendulum
import redis
import uuid

from sanic.response import text

import json

app = Sanic(__name__)

r = redis.StrictRedis(host=os.environ['REDIS_HOST'], port=6379)
db_conn = sqlite3.connect('falcon.db', check_same_thread=False)
db_cursor = db_conn.cursor()


@app.middleware('response')
async def print_on_response(request, response):
    print("I print when a response is returned by the server")
    asyncio.ensure_future(scan_redis_database())


async def scan_redis_database():
    for key in r.scan_iter():
        redis_item = r.get(key)
        python_item = eval(redis_item)
        print("------")
        print(python_item)
        print("--------")
        asyncio.ensure_future(insert_to_db(eval(key), json.dumps(python_item[0]), python_item[1]))
        r.delete(key)


@app.listener('after_server_start')
async def initialize_db(app, loop):
    r.flushdb()
    db_cursor.execute("DROP TABLE IF EXISTS DUMMY_JSON")
    db_cursor.execute("""CREATE TABLE DUMMY_JSON
                    (uuid TEXT, 
                    json_payload TEXT, 
                    timestamp_inserted_to_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                    timestamp_received TIMESTAMP)""")
    db_conn.commit()
    db_cursor.execute("INSERT INTO DUMMY_JSON VALUES ('1', 'Bla', '1', '2')")
    db_cursor.execute("SELECT * FROM DUMMY_JSON")
    print(db_cursor.fetchone())


async def insert_to_db(uuid, json_payload, timestap_received):
    params = (uuid, json_payload, timestap_received.to_datetime_string())
    print(params)
    print(type(json_payload))
    query = 'INSERT INTO DUMMY_JSON (uuid, json_payload, timestamp_received) VALUES (?, ?, ?);'
    db_cursor.execute(query, params)
    db_cursor.execute("SELECT * FROM DUMMY_JSON")
    print(db_cursor.fetchall())


@app.route("/json_dummy", methods=['PUT'])
async def put_json(request):
    timestamp_received = pendulum.now()
    json_content = request.json
    uuid_str = str(uuid.uuid4())
    r.set(uuid_str, (json_content, timestamp_received))
    bla = r.get(uuid_str)
    consumer = asyncio.ensure_future(insert_to_db(uuid_str, json_content, timestamp_received))
    return text("Received")


@app.route('/')
async def hello_world(request):
    return text('Hello World!!!')


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', port=5000, debug=True)