from telebot import TeleBot
from config import TELEGRAM_BOT_TOKEN


bot = TeleBot(TELEGRAM_BOT_TOKEN)
print(bot.get_me())
