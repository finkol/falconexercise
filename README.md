# Falcon.io Python Engineer Skills Assessment

The task is to implement a data processing pipeline in the cloud. Set up a running environment aligned with the technologies mentioned below:
* A Readme file containing information you deem useful for someone getting to know your code and want to try the system out
* Develop the application in Python 3
* A REST endpoint is taking a dummy JSON input, and the server puts the REST payload on Redis or another tool you think is well suited for the task
* A Consumer is running in the application, taking the freshly received message and persists it in a database of your choice
* A REST endpoint is implemented for retrieving all the messages persisted in JSON format from the database
* The message should also be pushed through Websockets for listening browser clients at the time the message was received on the REST endpoint
* A simple HTML page is implemented to show the real time message delivery
* Please setup a github repository to host the code and share it with your final note for review

## Prerequisites

[Docker](https://www.docker.com)

## Installing and running

This solution make use of docker-compose setup so with Docker installed and repository on local machine it's enough to 
put this in the terminal 

```
docker-compose up --build
```

given you're in the root of the solution. This should install and run the server.

## Using the solution

The server runs on port 3579 so the page to view the real time message delivery is accessible on [http://0.0.0.0:3579/]((http://0.0.0.0:3579/)).

These endpoints are available:
* To send JSON: PUT http://0.0.0.0:3579/json_dummy/ (JSON in the body)
* To get all JSON in the database: GET http://0.0.0.0:3579/json_dummy/
* To get one specific JSON: GET http://0.0.0.0:3579/json_dummy/[uuid] (without the brackets) 

Note that when the server is started Redis is flushed and the SQLite table is dropped and recreated, for quicker 
debugging and testing.

## Tests

Most aspects of the app are tested with several unit tests in tests/test_app.py.


## Built With

* [Sanic](https://github.com/channelcat/sanic) - The web framework used
* [aioredis](https://github.com/aio-libs/aioredis) - Redis library
* [SQLite3](http://sqlite.org/index.html) - Database used

## Authors

**Finnur Kolbeinsson**
