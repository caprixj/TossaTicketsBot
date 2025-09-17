import json
import uuid
from typing import Any, Union, Optional

from aiogram.types import CallbackQuery

from service.cbdata.encoding import decode_cbkey
from service.redis.redis_store import redis, CALLBACK_DATA_TTL


async def stash_payload(payload: dict[str, Any]) -> str:
    key = str(uuid.uuid4())
    await redis().set(
        name=key,
        value=json.dumps(payload),
        ex=CALLBACK_DATA_TTL
    )
    return key


async def peek_payload(src: Union[CallbackQuery, str]) -> Optional[dict[str, Any]]:
    if isinstance(src, CallbackQuery):
        key = decode_cbkey(src.data)
    elif isinstance(src, str):
        key = src
    else:
        raise TypeError('src must be CallbackQuery or str')

    data = await redis().get(key)
    return json.loads(data) if data else None
