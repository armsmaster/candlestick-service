from os import environ

from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker

redis_host = environ.get("REDIS_HOST")
redis_port = environ.get("REDIS_PORT")
redis_url = f"redis://{redis_host}:{redis_port}"


result_backend = RedisAsyncResultBackend(redis_url=redis_url)
broker = RedisStreamBroker(url=redis_url).with_result_backend(result_backend)
