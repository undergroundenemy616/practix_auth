import asyncio
import aioredis

from settings import Settings

config = Settings()


async def main():
    redis = await aioredis.create_redis_pool((config.redis_host, config.redis_port), minsize=10, maxsize=20)
    response = False
    while not response:
        print('redis ping')
        await asyncio.sleep(1)
        response = await redis.ping()
    print('the connection with redis service is established')
    redis.close()
    await redis.wait_closed()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
