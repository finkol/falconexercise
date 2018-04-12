import asynctest
import datetime

import pendulum

from app import app
from app.app import insert_to_db, select_all_from_db, initialize_db

import json as json_module


class TestDatabaseLayer(asynctest.TestCase):
    async def test_select_and_insert(self):
        # Begin with clean sheet
        loop = asynctest.asyncio.get_event_loop()
        await initialize_db(app, loop)

        # Select all rows from DB, should be empty
        results1 = await select_all_from_db()
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

        await insert_to_db(uuid, json_string, now)

        # Select all rows from DB, should have 1 row and values equal to above values
        results2 = await select_all_from_db()

        self.assertEqual(len(results2), 1)
        self.assertEqual(results2[0]['uuid'], uuid)
        self.assertEqual(json_module.dumps(results2[0]['data']), json_string)
        self.assertEqual(results2[0]['timestamp_received'], now.to_datetime_string())

        # Insert new row to db
        uuid2 = "024681012141618"
        now2 = pendulum.now()
        await insert_to_db(uuid2, json_string, now2)

        # Select all rows from DB, should have 2 rows and values equal to above values
        results3 = await select_all_from_db()

        self.assertEqual(len(results3), 2)
        self.assertEqual(results3[0]['uuid'], uuid)
        self.assertEqual(json_module.dumps(results3[0]['data']), json_string)
        self.assertEqual(results3[0]['timestamp_received'], now.to_datetime_string())
        self.assertEqual(results3[1]['uuid'], uuid2)
        self.assertEqual(json_module.dumps(results3[1]['data']), json_string)
        self.assertEqual(results3[1]['timestamp_received'], now2.to_datetime_string())

        # Insert same UUID as above, should not create duplicate
        await insert_to_db(uuid2, json_string, now2)

        # Select all rows from DB, should have 2 rows and values equal to above values
        results4 = await select_all_from_db()

        self.assertEqual(len(results4), 2)
        self.assertEqual(results4[0]['uuid'], uuid)
        self.assertEqual(json_module.dumps(results4[0]['data']), json_string)
        self.assertEqual(results4[0]['timestamp_received'], now.to_datetime_string())
        self.assertEqual(results4[1]['uuid'], uuid2)
        self.assertEqual(json_module.dumps(results4[1]['data']), json_string)
        self.assertEqual(results4[1]['timestamp_received'], now2.to_datetime_string())


if __name__ == '__main__':
    asynctest.main()
