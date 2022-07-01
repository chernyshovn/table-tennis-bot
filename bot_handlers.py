import random
import static.sticker_ids as sticker_ids
from bot import bot


@bot.message_handler(commands=['start'])
def handle_status_command(message):
    bot.send_message(message.chat.id, 'Вы подписались на бот!')


@bot.message_handler(commands=['status'])
def handle_status_command(message):
    sticker_id = random.choice([sticker_ids.happy_cat, sticker_ids.angry_bear])
    bot.send_message(message.chat.id, f'ID: {message.chat.id}')
    bot.send_sticker(message.chat.id, sticker_id)
