import random
import static.sticker_ids as sticker_ids
from bot import bot
from telebot import types
from database.database1 import db
from repositories.tournament_repository import TournamentRepository
from repositories.location_repository import LocationRepository


tournament_repository = TournamentRepository(db)
location_repository = LocationRepository(db)


@bot.message_handler(commands=['start'])
def handle_start_command(message):
    bot.send_message(message.chat.id, 'Вы подписались на бот!')


@bot.message_handler(commands=['status'])
def handle_status_command(message):
    sticker_id = random.choice([sticker_ids.happy_cat, sticker_ids.angry_bear])
    bot.send_message(message.chat.id, f'ID: {message.chat.id}')
    bot.send_sticker(message.chat.id, sticker_id)


@bot.message_handler(command=['start_single_match'])
def handle_start_single_match_command(message):
    user_id = message.chat.id
    if tournament_repository.has_active(user_id):
        print('У вас есть незавершенная игра!')
    else:
        bot.register_next_step_handler('Выберете локацию!', select_location)


def select_location(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for location in location_repository.list_all():
        markup.add(
            types.InlineKeyboardButton(
                location.name,
                callback_data=f'Location_{location.id}'
            )
        )
    bot.send_message(message.chat.id, 'Выберете локацию:', reply_markup=markup)


@bot.callback_query_handler(lambda query: query.data.startswith('Location_'))
def process_top_command_callback(query):
    location_id = int(query.data[len('Location_'):])
    bot.delete_message(query.message.chat.id, query.message.message_id)
    bot.send_message(query.message.chat.id, f'Location ID: {location_id}')


@bot.message_handler(command=['finish'])
def handle_finish_command(message):
    user_id = message.chat.id
    if tournament_repository.has_active(user_id):
        pass
    else:
        pass
