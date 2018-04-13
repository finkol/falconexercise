import json as json_module
import os
import sqlite3

import aioredis


# Note: SQLite is obviously not something I would suggest using in real application but it's easy to setup for
# this kind of exercise, while showing skills needed to communicate with more production ready database.

async def insert_to_db(app, uuid, json_payload, timestap_received):
    params = (uuid, json_payload, timestap_received.to_datetime_string())
    query = 'INSERT INTO dummy_json (uuid, json_payload, timestamp_received) VALUES (?, ?, ?);'
    app.db_cursor.execute(query, params)


async def select_all_from_db(app):
    app.db_cursor.execute("SELECT * FROM dummy_json")
    results = app.db_cursor.fetchall()
    dict_results = []
    for result in results:
        dict_result = dict(uuid=result[0], data=json_module.loads(result[1]), timestamp_inserted_to_db=result[2],
                           timestamp_received=result[3])
        dict_results.append(dict_result)

    return dict_results


async def select_one_from_db(app, uuid):
    query = "SELECT * FROM dummy_json WHERE uuid = ?"
    app.db_cursor.execute(query, (uuid,))
    result = app.db_cursor.fetchone()

    return dict(uuid=result[0], data=json_module.loads(result[1]), timestamp_inserted_to_db=result[2],
                timestamp_received=result[3])


async def initialize_db_and_redis(app, loop):
    # Start with clean sheet
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

    return app
