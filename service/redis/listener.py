from service.redis.redis_store import redis


async def start_redis_listener():
    r = redis()

    pubsub = r.pubsub()
    await pubsub.psubscribe('__keyevent@0__:expired')

    print('Listening for expired keys...')

    async for message in pubsub.listen():
        if message is None:
            continue
        if message['type'] == 'pmessage':
            expired_key = message['data']
            print(f'Expired key: {expired_key}')

            await handle_expiration(expired_key)


async def handle_expiration(key: str):
    # Example: cleanup, logging, or notifying some service
    print(f'Handling expiration for {key}')
    # implement business logic
