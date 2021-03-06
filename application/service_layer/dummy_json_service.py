import asyncio
import json as json_module
import pickle

from data_access_layer.dummy_json_dal import insert_to_db


async def proccess_json_in_redis(app, delete_after_getting=False, insert_to_db_after=True):
    # Scans the redis database and does what the input parameters say.
    async for key in app.r.iscan():
        redis_item = await app.r.get(key)

        if delete_after_getting:
            await app.r.delete(key)

        python_item = pickle.loads(redis_item)

        if insert_to_db_after:
            # Insert to database done in asynchronous non-blocking process
            asyncio.ensure_future(
                insert_to_db(app, key.decode("utf-8"), str(json_module.dumps(python_item[0])), python_item[1]))
        else:
            return dict(uuid=key.decode('utf-8'), data=json_module.dumps(python_item[0]),
                        timestamp_received=python_item[1].to_datetime_string())

    return None
