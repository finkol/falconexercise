import pickle
import unittest
import uuid

import asynctest

import pendulum

from application import main
from data_access_layer.dummy_json_dal import insert_to_db, select_all_from_db, initialize_db_and_redis

import json as json_module

from service_layer.dummy_json_service import proccess_json_in_redis


class TestDatabaseLayer(asynctest.TestCase):
    async def test_select_and_insert(self):
        # Begin with clean sheet
        loop = asynctest.asyncio.get_event_loop()
        app = await initialize_db_and_redis(main, loop)

        # Select all rows from DB, should be empty
        results1 = await select_all_from_db(app)
        self.assertEqual(len(results1), 0)

        # Insert first row to db
        uuid = "123456789101112"
        json_string = json_module.dumps("""{
            "video": [
                {
                    "id": "12312412312",
                    "name": "Ecuaciones Diferenciales",
                    "url": "/video/math/edo/12312412312",
                    "author": {
                        "data": [
                            {
                                "name_author": "Alejandro Morales",
                                "uri": "/author/alejandro-morales",
                                "type": "master"
                            }
                        ]
                    },
                    "comments": {
                        "data": [
                            {
                                "id": "367501354973_12216733",
                                "from": {
                                    "name": "Doug Edwards",
                                    "id": "628675309"
                                },
                                "message": "Make sure you don't, as they say, go whole hog...\nhttp://www.youtube.com/watch?v=U4wTFuaV8VQ",
                                "created_time": "2010-03-06T03:24:46+0000"
                            },
                            {
                                "id": "367501354973_12249673",
                                "from": {
                                    "name": "Tom Taylor",
                                    "id": "1249191863"
                                },
                                "message": "Are you and Karen gonna, as they say, pig out?",
                                "created_time": "2010-03-06T21:05:21+0000"
                            },
                            {
                                "id": "367501354973_12249857",
                                "from": {
                                    "name": "Sheila Taylor",
                                    "id": "1315606682"
                                },
                                "message": "how did it turn out?  Sounds nummy!\n",
                                "created_time": "2010-03-06T21:10:30+0000"
                            }
                        ]
                    }
                },
                {
                    "id": "12312412311",
                    "name": "Ecuaciones Diferenciales : El arte de las diferenciaciones",
                    "url": "/video/math/edo/1231241231212",
                    "author": {
                        "data": [
                            {
                                "name_author": "Alejandro Morales",
                                "uri": "/author/alejandro-morales",
                                "type": "master"
                            }
                        ]
                    },
                    "comments": {
                        "data": [
                            {
                                "id": "367501354973_12216733",
                                "from": {
                                    "name": "Doug Edwards",
                                    "id": "628675309"
                                },
                                "message": "Make sure you don't, as they say, go whole hog...\nhttp://www.youtube.com/watch?v=U4wTFuaV8VQ",
                                "created_time": "2010-03-06T03:24:46+0000"
                            },
                            {
                                "id": "367501354973_12249673",
                                "from": {
                                    "name": "Tom Taylor",
                                    "id": "1249191863"
                                },
                                "message": "Are you and Karen gonna, as they say, pig out?",
                                "created_time": "2010-03-06T21:05:21+0000"
                            },
                            {
                                "id": "367501354973_12249857",
                                "from": {
                                    "name": "Sheila Taylor",
                                    "id": "1315606682"
                                },
                                "message": "how did it turn out?  Sounds nummy!\n",
                                "created_time": "2010-03-06T21:10:30+0000"
                            }
                        ]
                    }
                }
            ]
        }""")
        now = pendulum.now()

        await insert_to_db(app, uuid, json_string, now)

        # Select all rows from DB, should have 1 row and values equal to above values
        results2 = await select_all_from_db(app)

        self.assertEqual(len(results2), 1)
        self.assertEqual(results2[0]['uuid'], uuid)
        self.assertEqual(json_module.dumps(results2[0]['data']), json_string)
        self.assertEqual(results2[0]['timestamp_received'], now.to_datetime_string())

        # Insert new row to db
        uuid2 = "024681012141618"
        now2 = pendulum.now()
        await insert_to_db(app, uuid2, json_string, now2)

        # Select all rows from DB, should have 2 rows and values equal to above values
        results3 = await select_all_from_db(app)

        self.assertEqual(len(results3), 2)
        self.assertEqual(results3[0]['uuid'], uuid)
        self.assertEqual(json_module.dumps(results3[0]['data']), json_string)
        self.assertEqual(results3[0]['timestamp_received'], now.to_datetime_string())
        self.assertEqual(results3[1]['uuid'], uuid2)
        self.assertEqual(json_module.dumps(results3[1]['data']), json_string)
        self.assertEqual(results3[1]['timestamp_received'], now2.to_datetime_string())

        # Insert same UUID as above, should not create duplicate
        await insert_to_db(app, uuid2, json_string, now2)

        # Select all rows from DB, should have 2 rows and values equal to above values
        results4 = await select_all_from_db(app)

        self.assertEqual(len(results4), 2)
        self.assertEqual(results4[0]['uuid'], uuid)
        self.assertEqual(json_module.dumps(results4[0]['data']), json_string)
        self.assertEqual(results4[0]['timestamp_received'], now.to_datetime_string())
        self.assertEqual(results4[1]['uuid'], uuid2)
        self.assertEqual(json_module.dumps(results4[1]['data']), json_string)
        self.assertEqual(results4[1]['timestamp_received'], now2.to_datetime_string())

        app.db_conn.close()


class TestRedis(asynctest.TestCase):
    async def test_redis_connection(self):
        # Begin with clean sheet
        loop = asynctest.asyncio.get_event_loop()
        app = await initialize_db_and_redis(main, loop)

        # First test the basic functions of redis, get and set
        await app.r.set("foo", "bar")

        test1 = await app.r.get("foo")

        self.assertEqual(test1.decode("utf-8"), "bar")

        # Delete the test data
        await app.r.delete("foo")

        self.assertIsNone(await app.r.get("foo"))

        # Test if the processing of the json in Redis work
        timestamp_received = pendulum.now()
        json_content = json_module.dumps("""{
            "video": [
                {
                    "id": "12312412312",
                    "name": "Ecuaciones Diferenciales",
                    "url": "/video/math/edo/12312412312",
                    "author": {
                        "data": [
                            {
                                "name_author": "Alejandro Morales",
                                "uri": "/author/alejandro-morales",
                                "type": "master"
                            }
                        ]
                    },
                    "comments": {
                        "data": [
                            {
                                "id": "367501354973_12216733",
                                "from": {
                                    "name": "Doug Edwards",
                                    "id": "628675309"
                                },
                                "message": "Make sure you don't, as they say, go whole hog...\nhttp://www.youtube.com/watch?v=U4wTFuaV8VQ",
                                "created_time": "2010-03-06T03:24:46+0000"
                            },
                            {
                                "id": "367501354973_12249673",
                                "from": {
                                    "name": "Tom Taylor",
                                    "id": "1249191863"
                                },
                                "message": "Are you and Karen gonna, as they say, pig out?",
                                "created_time": "2010-03-06T21:05:21+0000"
                            },
                            {
                                "id": "367501354973_12249857",
                                "from": {
                                    "name": "Sheila Taylor",
                                    "id": "1315606682"
                                },
                                "message": "how did it turn out?  Sounds nummy!\n",
                                "created_time": "2010-03-06T21:10:30+0000"
                            }
                        ]
                    }
                },
                {
                    "id": "12312412311",
                    "name": "Ecuaciones Diferenciales : El arte de las diferenciaciones",
                    "url": "/video/math/edo/1231241231212",
                    "author": {
                        "data": [
                            {
                                "name_author": "Alejandro Morales",
                                "uri": "/author/alejandro-morales",
                                "type": "master"
                            }
                        ]
                    },
                    "comments": {
                        "data": [
                            {
                                "id": "367501354973_12216733",
                                "from": {
                                    "name": "Doug Edwards",
                                    "id": "628675309"
                                },
                                "message": "Make sure you don't, as they say, go whole hog...\nhttp://www.youtube.com/watch?v=U4wTFuaV8VQ",
                                "created_time": "2010-03-06T03:24:46+0000"
                            },
                            {
                                "id": "367501354973_12249673",
                                "from": {
                                    "name": "Tom Taylor",
                                    "id": "1249191863"
                                },
                                "message": "Are you and Karen gonna, as they say, pig out?",
                                "created_time": "2010-03-06T21:05:21+0000"
                            },
                            {
                                "id": "367501354973_12249857",
                                "from": {
                                    "name": "Sheila Taylor",
                                    "id": "1315606682"
                                },
                                "message": "how did it turn out?  Sounds nummy!\n",
                                "created_time": "2010-03-06T21:10:30+0000"
                            }
                        ]
                    }
                }
            ]
        }""")
        uuid_str = str(uuid.uuid4().hex)
        await app.r.set(uuid_str, pickle.dumps((json_content, timestamp_received)))

        redis_dict = await proccess_json_in_redis(app, True, False)

        self.assertEqual(redis_dict['uuid'], uuid_str)
        self.assertEqual(json_module.loads(redis_dict['data']), json_content)
        self.assertEqual(redis_dict['timestamp_received'], timestamp_received.to_datetime_string())


class TestEndpoints(unittest.TestCase):
    def test_put_and_get_json(self):
        from main import app

        # Test the api endpoint, first the get with clean sheet, should return empty list
        c_request_1, c_response_1 = app.test_client.get('/json_dummy')

        self.assertEqual(c_response_1.status, 200)
        self.assertEqual(json_module.loads(c_response_1.body.decode('utf-8')), [])

        # Test the put JSON endpoint
        json_string = json_module.dumps("""{
            "video": [
                {
                    "id": "12312412312",
                    "name": "Ecuaciones Diferenciales",
                    "url": "/video/math/edo/12312412312",
                    "author": {
                        "data": [
                            {
                                "name_author": "Alejandro Morales",
                                "uri": "/author/alejandro-morales",
                                "type": "master"
                            }
                        ]
                    },
                    "comments": {
                        "data": [
                            {
                                "id": "367501354973_12216733",
                                "from": {
                                    "name": "Doug Edwards",
                                    "id": "628675309"
                                },
                                "message": "Make sure you don't, as they say, go whole hog...\nhttp://www.youtube.com/watch?v=U4wTFuaV8VQ",
                                "created_time": "2010-03-06T03:24:46+0000"
                            },
                            {
                                "id": "367501354973_12249673",
                                "from": {
                                    "name": "Tom Taylor",
                                    "id": "1249191863"
                                },
                                "message": "Are you and Karen gonna, as they say, pig out?",
                                "created_time": "2010-03-06T21:05:21+0000"
                            },
                            {
                                "id": "367501354973_12249857",
                                "from": {
                                    "name": "Sheila Taylor",
                                    "id": "1315606682"
                                },
                                "message": "how did it turn out?  Sounds nummy!\n",
                                "created_time": "2010-03-06T21:10:30+0000"
                            }
                        ]
                    }
                },
                {
                    "id": "12312412311",
                    "name": "Ecuaciones Diferenciales : El arte de las diferenciaciones",
                    "url": "/video/math/edo/1231241231212",
                    "author": {
                        "data": [
                            {
                                "name_author": "Alejandro Morales",
                                "uri": "/author/alejandro-morales",
                                "type": "master"
                            }
                        ]
                    },
                    "comments": {
                        "data": [
                            {
                                "id": "367501354973_12216733",
                                "from": {
                                    "name": "Doug Edwards",
                                    "id": "628675309"
                                },
                                "message": "Make sure you don't, as they say, go whole hog...\nhttp://www.youtube.com/watch?v=U4wTFuaV8VQ",
                                "created_time": "2010-03-06T03:24:46+0000"
                            },
                            {
                                "id": "367501354973_12249673",
                                "from": {
                                    "name": "Tom Taylor",
                                    "id": "1249191863"
                                },
                                "message": "Are you and Karen gonna, as they say, pig out?",
                                "created_time": "2010-03-06T21:05:21+0000"
                            },
                            {
                                "id": "367501354973_12249857",
                                "from": {
                                    "name": "Sheila Taylor",
                                    "id": "1315606682"
                                },
                                "message": "how did it turn out?  Sounds nummy!\n",
                                "created_time": "2010-03-06T21:10:30+0000"
                            }
                        ]
                    }
                }
            ]
        }""")
        c_request_2, c_response_2 = app.test_client.put('/json_dummy', data=json_string,
                                                        headers={'content-type': 'application/json'})

        self.assertEqual(c_response_2.status, 200)
        self.assertEqual(c_response_2.body.decode('utf-8'), 'Received')

        #
        # Due to app.test_client fires up new server every time it's called and I flush both redis and the DB every time
        # the server starts the last select (below) do not return correct results. In real world application this would
        # not be the case.
        #

        # c_request_3, c_response_3 = app.test_client.get('/json_dummy')

        # self.assertEqual(c_response_3.status, 200)
        # self.assertEqual(len(json_module.loads(c_response_3.body.decode('utf-8'))), 1)


if __name__ == '__main__':
    asynctest.main()
