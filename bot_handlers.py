import re
from datetime import timedelta
from typing import Optional
from bot import bot
from telebot import types
from database.database import db
from decorators.validation_decorator import validate_user
from enums.telegram_user_state import TelegramUserState
from enums.match_result import MatchResult
from services.static.sticker_ids import StickerIds
from services.common.telegram_user_manager import TelegramUserManager
from services.common.tournament_manager import TournamentManager
from services.common.location_manager import LocationManager
from services.common.player_manager import PlayerManager
from services.common.match_score_provider import MatchScoreProvider
from services.telegram_user_state_provider import TelegramUserStateProvider
from services.single_match.single_match_player_adder import SingleMatchPlayerAdder
from services.single_match.single_match_match_manager import SingleMatchMatchManager
from services.single_match.single_match_player_names_provider import SingleMatchPlayerNameProvider
from services.single_match.single_match_game_adder import SingleMatchGameAdder
from services.single_match.single_match_telegram_statistic_provider import SingleMatchTelegramStatisticProvider
from services.single_match.single_match_elo_rate_manager import SingleMatchEloRateManager


telegram_user_manager = TelegramUserManager()
telegram_user_state_manager = TelegramUserStateProvider(db)
tournament_manager = TournamentManager(db)
location_manager = LocationManager(db)
player_manager = PlayerManager(db)
match_score_provider = MatchScoreProvider()
single_match_player_adder = SingleMatchPlayerAdder(db)
single_match_game_adder = SingleMatchGameAdder(db)
single_match_match_manager = SingleMatchMatchManager(db)
single_match_player_names_provider = SingleMatchPlayerNameProvider(db)
single_match_telegram_statistic_provider = SingleMatchTelegramStatisticProvider(db, timedelta(hours=3))
single_match_elo_rate_manager = SingleMatchEloRateManager(db, player_manager)


@bot.message_handler(commands=['start'])
def handle_start_command(message):
    bot.send_message(message.chat.id, '?????????? ???????????????????? ?? ??????!')


@bot.message_handler(commands=['status'])
def handle_status_command(message):
    bot.send_message(message.chat.id, f'User ID: {message.from_user.id}\nChat ID: {message.chat.id}')


@bot.message_handler(commands=['start_single_match'])
@validate_user
def handle_start_single_match_command(message):
    user_id = message.chat.id
    if tournament_manager.has_active(user_id):
        bot.send_message(message.chat.id, '?? ?????? ???????? ?????????????????????????? ????????!')
    else:
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        for location in location_manager.list_all():
            buttons.append(
                types.InlineKeyboardButton(
                    location.name,
                    callback_data=f'Location_{location.id}'
                )
            )
        markup.add(*buttons)
        bot.send_message(message.chat.id, '???????????????? ??????????????:', reply_markup=markup)


@bot.callback_query_handler(lambda query: query.data.startswith('Location_'))
def process_add_location_callback(query):
    chat_id = query.message.chat.id

    pattern = re.compile(r"Location_(\d+)")
    match = pattern.search(query.data)
    location_id = int(match.group(1))

    location_name = location_manager.get_name_by_id(location_id)
    bot.delete_message(chat_id, query.message.message_id)
    tournament_manager.create(location_id, chat_id)
    bot.send_message(chat_id, f'??????????????: ??{location_name}??!')

    select_player(query.message, 1)


def select_player(message, player_number: int):
    chat_id = message.chat.id
    tournament_id = tournament_manager.get_active_id(message.chat.id)

    if player_number <= 2:
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        for player in player_manager.list_not_in_tournament(tournament_id):
            buttons.append(
                types.InlineKeyboardButton(
                    player.name,
                    callback_data=f'Player_{player.id}_{player_number}'
                )
            )
        markup.add(*buttons)
        bot.send_message(chat_id, f'???????????????? ???????????? ???{player_number}:', reply_markup=markup)
    else:
        match_id = single_match_match_manager.add(tournament_id)
        player_names = single_match_player_names_provider.get(match_id)

        telegram_user_state_manager.set(chat_id, TelegramUserState.MATCH_IN_PROGRESS)
        bot.send_sticker(chat_id, StickerIds.gagarin)
        bot.send_message(chat_id, f'???????? ??????????! ?????????????? ???????? ?????????? ?? ?????????????? ??{player_names[0]} - {player_names[1]}??:')


@bot.message_handler(func=lambda message: telegram_user_state_manager.get(message.chat.id) == TelegramUserState.MATCH_IN_PROGRESS)
@validate_user
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
            if score1 != score2:
                match_id = single_match_match_manager.get_active_id(chat_id)
                single_match_game_adder.add(chat_id, score1, score2)
                player_names = single_match_player_names_provider.get(match_id)
                first_player_name = player_names[0]
                second_player_name = player_names[1]
                match_score = match_score_provider.get(match_id)
                msg_text = f'<b>{first_player_name} {score1} - {score2} {second_player_name}</b>\n\n'
                msg_text += '<b>?????????????? ???????? ???? ????????????:</b>\n'
                msg_text += f'{first_player_name} {match_score.first_team_score} - {match_score.second_team_score} {second_player_name}\n\n'
                msg_text += '?????????????? ???????? ???????????????????? ?????????? ?????? ?????????????????? ?????????????? /finish_match ?????? ???????????????????? ????????!'
                bot.send_message(chat_id, msg_text, parse_mode='html')
            else:
                send_invalid_command_message(chat_id, '???????? ???? ?????????? ???????? ????????????! ?????????????? ?????? ??????!')
        else:
            send_invalid_command_message(chat_id, '???????????????????? ???????????? ??????????! ?????????????? ?????? ??????!')


@bot.callback_query_handler(lambda query: query.data.startswith('Player_'))
def process_add_player_callback(query):
    chat_id = query.message.chat.id

    pattern = re.compile(r"Player_(\d+)_(\d+)")
    match = pattern.search(query.data)
    player_id = int(match.group(1))
    player_number = int(match.group(2))

    player_name = player_manager.get_name_by_id(player_id)
    bot.delete_message(chat_id, query.message.message_id)

    tournament_id = tournament_manager.get_active_id(chat_id)
    single_match_player_adder.add(tournament_id, player_id)

    bot.send_message(chat_id, f'?????????? ???{player_number}: {player_name}!')

    select_player(query.message, player_number + 1)


def rate_change_to_string(player_name: str, old_value: int, new_value: int) -> str:
    diff = new_value - old_value
    return f'{player_name}: {old_value} ??? {new_value} ({diff:+})'


@bot.message_handler(commands=['finish_match'])
@validate_user
def handle_finish_match_command(message):
    user_id = message.chat.id
    telegram_user_state_manager.set(user_id, None)
    tournament_id = tournament_manager.get_active_id(user_id)
    match_id = single_match_match_manager.get_active_id(user_id)

    if (not tournament_id) and (not match_id):
        bot.send_message(user_id, '?? ?????? ?????? ?????????????????????????? ????????????!')
        return

    if tournament_id:
        tournament_manager.set_end_date_time(tournament_id)
    if match_id:
        single_match_match_manager.finish_match(match_id)

    match_statistic = single_match_telegram_statistic_provider.ensure_and_get(tournament_id)

    if match_statistic.is_no_games():
        tournament_manager.delete(tournament_id)
        bot.send_message(user_id, '???? ???? ?????????????? ???? ???????????? ??????????!')
        bot.send_sticker(user_id, StickerIds.boor)
        return

    elo_rate_updating_result = single_match_elo_rate_manager.update(
        match_id=match_id,
        player_1_id=match_statistic.player_1_id,
        player_2_id=match_statistic.player_2_id,
        player_1_game_won_count=match_statistic.player_1_games_won,
        player_2_game_won_count=match_statistic.player_2_games_won,
        date_time=match_statistic.end_date_time
    )

    rate_change_text = f'<b>?????????????????? ????????????????</b>\n\n' + rate_change_to_string(
                           match_statistic.player_1_name,
                           elo_rate_updating_result.player_1_old_rate,
                           elo_rate_updating_result.player_1_new_rate
                       ) + '\n' + rate_change_to_string(
                           match_statistic.player_2_name,
                           elo_rate_updating_result.player_2_old_rate,
                           elo_rate_updating_result.player_2_new_rate
                       )

    chat_ids = {user_id, match_statistic.player_1_telegram_id, match_statistic.player_2_telegram_id}
    chat_ids.update(telegram_user_manager.list_subscribed_to_all_notifications())

    for chat_id in chat_ids:
        if chat_id:
            try:
                bot.send_message(chat_id, match_statistic.description, parse_mode='html')

                player_number: Optional[int] = None
                if match_statistic.player_1_telegram_id == chat_id:
                    player_number = 1
                elif match_statistic.player_2_telegram_id == chat_id:
                    player_number = 2

                if player_number:
                    text: Optional[str] = None
                    sticker_id: Optional[str] = None
                    if ((match_statistic.result == MatchResult.FIRST_PLAYER_WON) and (player_number == 1)) or\
                            ((match_statistic.result == MatchResult.SECOND_PLAYER_WON) and (player_number == 2)):
                        text = '???? ????????????????! ????'
                        sticker_id = StickerIds.happy_cat
                    elif ((match_statistic.result == MatchResult.FIRST_PLAYER_WON) and (player_number == 2)) or\
                            ((match_statistic.result == MatchResult.SECOND_PLAYER_WON) and (player_number == 1)):
                        text = '???? ??????????????????! ????'
                        sticker_id = StickerIds.angry_bear
                    elif match_statistic.result == MatchResult.DRAW:
                        text = '??????????! ????'
                        sticker_id = StickerIds.idk_desman

                    if text:
                        bot.send_message(chat_id, text)

                    if sticker_id:
                        bot.send_sticker(chat_id, sticker_id)

                bot.send_message(chat_id, rate_change_text, parse_mode='html')
            except:
                pass


@bot.message_handler(commands=['elo_rating'])
@validate_user
def handle_elo_rating_command(message):
    rates = single_match_elo_rate_manager.list()
    text = '?????????????? ?????????????? ??????:\n\n'
    for index, rate in enumerate(rates):
        text += f'{index + 1}. {rate.value} - {rate.player_name}\n'
    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda message: message.text.strip().startswith('-create-player'))
@validate_user
def handle_create_player_command(message):
    pattern = re.compile(r"^\s*-create-player\s+(.+)\s*$")
    regex_match = pattern.search(message.text)
    if regex_match:
        chat_id = message.chat.id
        name = str(regex_match.group(1))
        player = player_manager.get_by_name(name)
        if not player:
            player_manager.create(name)
            bot.send_message(chat_id, f'?????????? ??{name}?? ????????????????!')
        elif not player.is_active:
            player_manager.update_is_active(player.id, True)
            bot.send_message(chat_id, f'?????????? ??{name}?? ?????? ????????????????????, ???? ?????? ???? ??????????????! ???????????? ???? ???????????????? ?????? ???????????????? ??????????/??????????????!')
        else:
            bot.send_message(chat_id, f'?????????? ??{name}?? ?????? ????????????????????!')
    else:
        handle_unsupported_command(message)


@bot.message_handler(func=lambda message: True)
def handle_unsupported_command(message):
    send_invalid_command_message(message.chat.id, '???????????????????????????????? ??????????????!')


def send_invalid_command_message(chat_id, text: str) -> None:
    bot.send_message(chat_id, text)
    bot.send_sticker(chat_id, StickerIds.angry_punica)
