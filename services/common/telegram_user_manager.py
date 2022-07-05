from app import app
from database.models import TelegramUser


class TelegramUserManager:
    @staticmethod
    def has_access(chat_id: int) -> bool:
        with app.app_context():
            user = TelegramUser.query.get(chat_id)
            return user.has_access if user else False

    @staticmethod
    def list_subscribed_to_all_notifications() -> list[int]:
        with app.app_context():
            users = TelegramUser.query.filter_by(subscribed_to_all_notifications=True)
            return [user.chat_id for user in users]
