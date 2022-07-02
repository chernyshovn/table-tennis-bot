from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config import TELEGRAM_BOT_TOKEN


storage = StateMemoryStorage()
bot = TeleBot(TELEGRAM_BOT_TOKEN, state_storage=storage)

print(bot.get_me())
