import ast
import pickle

import aioredis
from sanic import Sanic
import asyncio
import os
import sqlite3

import pendulum
import redis
import uuid

from sanic.response import text, json, file

import json as json_module

app = Sanic(__name__)

# r = redis.StrictRedis(host=os.environ['REDIS_HOST'], port=6379)
db_conn = sqlite3.connect('falcon.db', check_same_thread=False)
db_cursor = db_conn.cursor()


@app.middleware('response')
async def consumer(request, response):
    asyncio.ensure_future(scan_redis_database(request))


async def scan_redis_database(request):
    async for key in request.app.r.iscan():
        redis_item = await request.app.r.get(key)
        python_item = pickle.loads(redis_item)
        asyncio.ensure_future(insert_to_db(key.decode("utf-8"), str(json_module.dumps(python_item[0])), python_item[1]))


@app.listener('after_server_start')
async def initialize_db(app, loop):
    # Start with an empty sheet
    app.r = await aioredis.create_redis_pool((os.environ['REDIS_HOST'], 6379))
    app.r.iscan()
    await app.r.flushall()
    db_cursor.execute("DROP TABLE IF EXISTS dummy_json")
    db_cursor.execute("""CREATE TABLE dummy_json
                    (uuid TEXT, 
                    json_payload TEXT, 
                    timestamp_inserted_to_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                    timestamp_received TIMESTAMP,
                    UNIQUE(uuid) ON CONFLICT REPLACE)""")
    db_conn.commit()


@app.listener('after_server_stop')
async def cleanup(app, loop):
    # gracefully closing underlying connection
    app.r.close()
    await app.r.wait_closed()


async def insert_to_db(uuid, json_payload, timestap_received):
    params = (uuid, json_payload, timestap_received.to_datetime_string())
    query = 'INSERT INTO dummy_json (uuid, json_payload, timestamp_received) VALUES (?, ?, ?);'
    db_cursor.execute(query, params)
    db_cursor.execute("SELECT * FROM dummy_json")
    print(db_cursor.fetchall())


async def select_all_from_db():
    db_cursor.execute("SELECT * FROM dummy_json")
    results = db_cursor.fetchall()
    dict_results = []
    for result in results:
        dict_result = dict(uuid=result[0], data=json_module.loads(result[1]), timestamp_inserted_to_db=result[2],
                           timestamp_received=result[3])
        dict_results.append(dict_result)

    return dict_results


async def select_one_from_db(uuid):
    query = "SELECT * FROM dummy_json WHERE uuid = ?"
    db_cursor.execute(query, (uuid,))
    result = db_cursor.fetchone()

    return dict(uuid=result[0], data=json_module.loads(result[1]), timestamp_inserted_to_db=result[2],
                timestamp_received=result[3])


@app.put("/json_dummy")
async def put_json(request):
    timestamp_received = pendulum.now()
    json_content = request.json
    uuid_str = str(uuid.uuid4().hex)
    await request.app.r.set(uuid_str, pickle.dumps((json_content, timestamp_received)))
    return text("Received")


@app.get("/json_dummy")
async def get_json(request):
    return json(await select_all_from_db())


@app.get("/json_dummy/<uuid>")
async def get_one_json(request, uuid):
    return json(await select_one_from_db(uuid))


@app.websocket('/json_dummy_ws')
async def socket_json(request, ws):
    while True:
        async for key in request.app.r.iscan():
            print(key)
            redis_item = await request.app.r.get(key)
            await request.app.r.delete(key)
            python_item = pickle.loads(redis_item)
            await ws.send(json_module.dumps(dict(uuid=key.decode('utf-8'), data=json_module.dumps(python_item[0]),
                                                 timestamp_received=python_item[1].to_datetime_string())))


@app.route('/')
async def render_index(request):
    return await file('templates/index.html')


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', port=5000, debug=True)
