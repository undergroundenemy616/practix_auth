import asyncio

from elasticsearch import AsyncElasticsearch

from settings import Settings

config = Settings()


async def main():
    es = AsyncElasticsearch(hosts=[f'{config.es_host}:{config.es_port}'])
    response = False
    while not response:
        print('elastic ping')
        await asyncio.sleep(1)
        response = await es.ping()
    print('the connection with elasticsearch service is established')
    await es.close()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
