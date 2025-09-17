from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

def _is_command(msg):
    ents = msg.entities or []
    for e in ents:
        if e.type == 'bot_command' and e.offset == 0:
            return True
    # Fallback
    return bool(msg.text and msg.text.startswith('/'))

class PreemptFSMContextInPrivateMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        if not (isinstance(event, Message) and _is_command(event)):
            return await handler(event, data)

        if event.chat.type != 'private':
            return await handler(event, data)

        state = data.get('state')
        if not state:
            return await handler(event, data)

        current = await state.get_state()
        if current is not None:
            # abort any running flow
            await state.clear()

        return await handler(event, data)
