import re
import random
import static.sticker_ids as sticker_ids
from bot import bot
from telebot import types
from database.database import db
from enums.telegram_user_state import TelegramUserState
from repositories.tournament_repository import TournamentRepository
from repositories.location_repository import LocationRepository
from repositories.player_repository import PlayerRepository
from services.telegram_user_state_provider import TelegramUserStateProvider
from services.single_match_player_adder import SingleMatchPlayerAdder
from services.single_match_match_adder import SingleMatchMatchAdder
from services.single_match_player_names_provider import SingleMatchPlayerNameProvider
from services.single_match_game_adder import SingleMatchGameAdder
from services.single_match_statistic_provider import SingleMatchStatisticProvider


telegram_user_state_manager = TelegramUserStateProvider(db)
tournament_repository = TournamentRepository(db)
location_repository = LocationRepository(db)
player_repository = PlayerRepository(db)
single_match_player_adder = SingleMatchPlayerAdder(db)
single_match_game_adder = SingleMatchGameAdder(db)
single_match_match_adder = SingleMatchMatchAdder(db)
single_match_player_names_provider = SingleMatchPlayerNameProvider(db)
single_match_statistic_provider = SingleMatchStatisticProvider(db)


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
        bot.send_message(message.chat.id, 'У вас есть незавершенная игра!')
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

    pattern = re.compile(r"Location_(\d+)")
    match = pattern.search(query.data)
    location_id = int(match.group(1))

    location_name = location_repository.get_name_by_id(location_id)
    bot.delete_message(chat_id, query.message.message_id)
    tournament_repository.create(location_id, chat_id)
    bot.send_message(chat_id, f'Локация: «{location_name}»!')

    select_player(query.message, 1)


def select_player(message, player_number: int):
    if player_number <= 2:
        markup = types.InlineKeyboardMarkup(row_width=1)
        for player in player_repository.list_all():
            markup.add(
                types.InlineKeyboardButton(
                    player.name,
                    callback_data=f'Player_{player.id}_{player_number}'
                )
            )
        bot.send_message(message.chat.id, f'Выберете игрока №{player_number}:', reply_markup=markup)
    else:
        tournament_id = tournament_repository.get_active_id(message.chat.id)
        match_id = single_match_match_adder.add(tournament_id)
        player_names = single_match_player_names_provider.get(match_id)

        telegram_user_state_manager.set(message.chat.id, TelegramUserState.MATCH_IN_PROGRESS)
        bot.send_message(message.chat.id, f'Матч начат! Введите счет гейма в формате «{player_names[0]} - {player_names[1]}»:')


@bot.message_handler(func=lambda message: telegram_user_state_manager.get(message.chat.id) == TelegramUserState.MATCH_IN_PROGRESS)
def handle_match_in_progress(message):
    command: str = message.text
    chat_id = message.chat.id

    if command == '/finish_match':
        handle_finish_match_command(message)
    else:
        pattern = re.compile(r"^\D*(\d+)\D+(\d+)\D*$")
        re_match = pattern.search(command)
        if re_match:
            score1 = int(re_match.group(1))
            score2 = int(re_match.group(2))
            single_match_game_adder.add(chat_id, score1, score2)
            match_id = single_match_match_adder.get_active_id(chat_id)
            player_names = single_match_player_names_provider.get(match_id)
            msg_text = f'{player_names[0]} {score1} - {score2} {player_names[1]}\n\n'
            msg_text += 'Введите счет следующего гейма или выполните команду /finish_match для завершения игры!'
        else:
            msg_text = 'Невалидный формат счета! Введите еще раз!'
        bot.send_message(chat_id, msg_text)


@bot.callback_query_handler(lambda query: query.data.startswith('Player_'))
def process_add_player_callback(query):
    chat_id = query.message.chat.id

    pattern = re.compile(r"Player_(\d+)_(\d+)")
    match = pattern.search(query.data)
    player_id = int(match.group(1))
    player_number = int(match.group(2))

    player_name = player_repository.get_name_by_id(player_id)
    bot.delete_message(chat_id, query.message.message_id)

    tournament_id = tournament_repository.get_active_id(chat_id)
    single_match_player_adder.add(tournament_id, player_id)

    bot.send_message(chat_id, f'Игрок №{player_number}: {player_name}!')

    select_player(query.message, player_number + 1)


@bot.message_handler(commands=['finish_match'])
def handle_finish_match_command(message):
    user_id = message.chat.id
    telegram_user_state_manager.set(user_id, None)
    tournament_id = tournament_repository.get_active_id(user_id)
    match_id = single_match_match_adder.get_active_id(user_id)

    if (not tournament_id) and (not match_id):
        bot.send_message(user_id, 'У вас нет незавершенных матчей!')
    else:
        if tournament_id:
            tournament_repository.set_end_date_time(tournament_id)
        if match_id:
            single_match_match_adder.finish_match(match_id)

        match_statistic = single_match_statistic_provider.get(tournament_id)
        bot.send_message(user_id, match_statistic, parse_mode='html')
