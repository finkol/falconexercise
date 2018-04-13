import pickle

from sanic import Sanic
import asyncio

import pendulum
import uuid

from sanic.response import text, json, file

import json as json_module

from data_access_layer.dummy_json_dal import initialize_db_and_redis, select_all_from_db, select_one_from_db
from service_layer.dummy_json_service import proccess_json_in_redis

app = Sanic(__name__)


@app.middleware('response')
async def consumer(request, response):
    # This run after each request to the server.
    asyncio.ensure_future(proccess_json_in_redis(request.app, False, True))


@app.listener('after_server_start')
async def init(app, loop):
    # Run right after the server starts
    await initialize_db_and_redis(app, loop)


@app.listener('after_server_stop')
async def cleanup(app, loop):
    # gracefully closing underlying connection
    app.r.close()
    await app.r.wait_closed()


@app.put("/json_dummy")
async def put_json(request):
    # Endpoint to insert json. It inserts first to redis. Then the consumer picks it up to insert to database
    timestamp_received = pendulum.now()
    json_content = request.json
    uuid_str = str(uuid.uuid4().hex)
    await request.app.r.set(uuid_str, pickle.dumps((json_content, timestamp_received)))
    return text("Received")


@app.get("/json_dummy")
async def get_json(request):
    # Returns all json in the database
    return json(await select_all_from_db(request.app))


@app.get("/json_dummy/<uuid>")
async def get_one_json(request, uuid):
    # Returns one json for given uuid
    return json(await select_one_from_db(request.app, uuid))


@app.websocket('/json_dummy_ws')
async def socket_json(request, ws):
    while True:
        redis_dict = await proccess_json_in_redis(request.app, True, False)
        if redis_dict is not None:
            await ws.send(json_module.dumps(redis_dict))


@app.route('/')
async def render_index(request):
    return await file('application/templates/index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3579)
