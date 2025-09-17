# import json
# import uuid
# from typing import Any, Optional, Union
#
# from aiogram.types import CallbackQuery, Message
#
# from resources import glob
# from service.redis.redis_store import redis, FLOW_SESSION_TTL
#
#
# def k_flow(user_id: int, chat_id: int) -> str:
#     """ Form a flow session key (ucid) """
#     return f'{user_id}:{chat_id}'
#
#
# async def start_flow(user_id: int, chat_id: int, flow_name: str) -> dict[str, Any]:
#     val = {
#         'name': flow_name,
#         'session_id': str(uuid.uuid4())
#     }
#     await redis().set(
#         name=k_flow(user_id, chat_id),
#         value=json.dumps(val),
#         ex=FLOW_SESSION_TTL
#     )
#     return val
#
#
# async def get_flow(user_id: int, chat_id: int) -> Optional[dict[str, Any]]:
#     s = await redis().get(k_flow(user_id, chat_id))
#     return json.loads(s) if s else None
#
#
# async def ensure_flow(src: Union[CallbackQuery, Message], payload: dict[str, Any]) -> bool:
#     async def error():
#         await src.answer(glob.FLOW_SESSION_EXPIRED, show_alert=True)
#
#     payload_sess = payload.get('flow_session_id')
#     last_sess = await get_flow(src.from_user.id, src.chat.id)
#     # бд загальна і для пп, і для груп
#     # тому треба порівнювати й юсіди напевно
#     # аби вони не перетиналися
#     #
#     if payload_sess == last_sess:
#         await error()
#         return False
#
#     return True