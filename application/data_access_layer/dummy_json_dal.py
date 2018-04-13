import json as json_module
import os
import sqlite3

import aioredis


async def insert_to_db(request, uuid, json_payload, timestap_received):
    params = (uuid, json_payload, timestap_received.to_datetime_string())
    query = 'INSERT INTO dummy_json (uuid, json_payload, timestamp_received) VALUES (?, ?, ?);'
    request.app.db_cursor.execute(query, params)


async def select_all_from_db(request):
    request.app.db_cursor.execute("SELECT * FROM dummy_json")
    results = request.app.db_cursor.fetchall()
    dict_results = []
    for result in results:
        dict_result = dict(uuid=result[0], data=json_module.loads(result[1]), timestamp_inserted_to_db=result[2],
                           timestamp_received=result[3])
        dict_results.append(dict_result)

    return dict_results


async def select_one_from_db(request, uuid):
    query = "SELECT * FROM dummy_json WHERE uuid = ?"
    request.app.db_cursor.execute(query, (uuid,))
    result = request.app.db_cursor.fetchone()

    return dict(uuid=result[0], data=json_module.loads(result[1]), timestamp_inserted_to_db=result[2],
                timestamp_received=result[3])


async def initialize_db_and_redis(app, loop):
    # Start with an empty sheet
    try:
        app.r = await aioredis.create_redis_pool((os.environ['REDIS_HOST'], 6379))
    except:
        app.r = await aioredis.create_redis_pool(("127.0.0.1", 6379))
    await app.r.flushall()

    app.db_conn = sqlite3.connect('falcon.db', check_same_thread=False)
    app.db_cursor = app.db_conn.cursor()

    app.db_cursor.execute("DROP TABLE IF EXISTS dummy_json")
    app.db_cursor.execute("""CREATE TABLE dummy_json
                    (uuid TEXT, 
                    json_payload TEXT, 
                    timestamp_inserted_to_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                    timestamp_received TIMESTAMP,
                    UNIQUE(uuid) ON CONFLICT REPLACE)""")
    app.db_conn.commit()
