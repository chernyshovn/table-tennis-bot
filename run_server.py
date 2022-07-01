import os
import flask
from flask_sqlalchemy import SQLAlchemy
from telebot import types
from bot_handlers import bot
from config import APP_SECRET, APP_NAME, DB_CONNECTION_STRING, TELEGRAM_BOT_TOKEN


server = flask.Flask(__name__)
server.config['SECRET_KEY'] = APP_SECRET
server.config['SQLALCHEMY_DATABASE_URI'] = DB_CONNECTION_STRING

db = SQLAlchemy(server)


@server.route('/' + TELEGRAM_BOT_TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates([types.Update.de_json(flask.request.stream.read().decode('utf-8'))])
    return '!', 200


@server.route('/', methods=['GET'])
def index():
    bot.remove_webhook()
    bot.set_webhook(url='https://{}.herokuapp.com/{}'.format(APP_NAME, TELEGRAM_BOT_TOKEN))
    return 'Hello from Telegram Bot!', 200


if __name__ == '__main__':
    server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
