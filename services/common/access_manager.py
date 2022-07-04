from app import app
from database.models import TelegramUser


class AccessManager:
    @staticmethod
    def has_access(chat_id: int) -> bool:
        with app.app_context():
            user = TelegramUser.query.get(chat_id)
            return user.has_access if user else False
