from functools import wraps
from bot import bot
from services.common.access_manager import AccessManager


def validate_user(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        chat_id = args[0].chat.id
        if AccessManager.has_access(chat_id):
            fn(*args, **kwargs)
        else:
            bot.send_message(chat_id, 'No access!')
    return wrapped
