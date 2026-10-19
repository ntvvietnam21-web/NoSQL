import redis
from flask import current_app


def init_redis(app):
    client = redis.Redis(
        host=app.config["REDIS_HOST"],
        port=app.config["REDIS_PORT"],
        db=app.config["REDIS_DB"],
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
    )
    app.extensions["redis"] = client


def get_redis():
    return current_app.extensions["redis"]
