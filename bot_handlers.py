import random
import static.sticker_ids as sticker_ids
from bot import bot
from telebot import types
from database.database import db
from repositories.tournament_repository import TournamentRepository
from repositories.location_repository import LocationRepository
from repositories.player_repository import PlayerRepository


tournament_repository = TournamentRepository(db)
location_repository = LocationRepository(db)
player_repository = PlayerRepository(db)


@bot.message_handler(commands=['start'])
def handle_start_command(message):
    bot.send_message(message.chat.id, 'Вы подписались на бот!')


@bot.message_handler(commands=['status'])
def handle_status_command(message):
    sticker_id = random.choice([sticker_ids.happy_cat, sticker_ids.angry_bear])
    bot.send_message(message.chat.id, f'ID: {message.chat.id}')
    bot.send_sticker(message.chat.id, sticker_id)


@bot.message_handler(commands=['start_single_match'])
def handle_start_single_match_command(message):
    user_id = message.chat.id
    if tournament_repository.has_active(user_id):
        print('У вас есть незавершенная игра!')
    else:
        markup = types.InlineKeyboardMarkup(row_width=2)
        for location in location_repository.list_all():
            markup.add(
                types.InlineKeyboardButton(
                    location.name,
                    callback_data=f'Location_{location.id}'
                )
            )
        bot.send_message(message.chat.id, 'Выберете локацию:', reply_markup=markup)


@bot.callback_query_handler(lambda query: query.data.startswith('Location_'))
def process_add_location_callback(query):
    chat_id = query.message.chat.id
    location_id = int(query.data[len('Location_'):])
    location_name = location_repository.get_name_by_id(location_id)
    bot.delete_message(chat_id, query.message.message_id)
    tournament_repository.create(location_id, chat_id)
    bot.send_message(chat_id, f'Вы выбрали локацию «{location_name}»!')

    select_player(chat_id, 1)


def select_player(chat_id: int, player_number: int):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for player in player_repository.list_all():
        markup.add(
            types.InlineKeyboardButton(
                player.name,
                callback_data=f'Player_{player.id}'
            )
        )
    bot.send_message(chat_id, f'Выберете игрока №{player_number}:', reply_markup=markup)


@bot.callback_query_handler(lambda query: query.data.startswith('Player_'))
def process_add_player_callback(query):
    chat_id = query.message.chat.id
    player_id = int(query.data[len('Player_'):])
    player_name = player_repository.get_name_by_id(player_id)
    bot.delete_message(chat_id, query.message.message_id)
    # todo: add to repo
    bot.send_message(chat_id, f'Игрок №1: «{player_name}»!')

    select_player(chat_id, 2)


@bot.message_handler(command=['finish'])
def handle_finish_command(message):
    user_id = message.chat.id
    if tournament_repository.has_active(user_id):
        pass
    else:
        pass
