import os
import flask
from telebot import types
from app import app
from bot_handlers import bot
from database.database import db
from config import APP_SECRET, APP_NAME, DB_CONNECTION_STRING, TELEGRAM_BOT_TOKEN

app.config['SECRET_KEY'] = APP_SECRET
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONNECTION_STRING
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


@app.route('/' + TELEGRAM_BOT_TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates([types.Update.de_json(flask.request.stream.read().decode('utf-8'))])
    return '!', 200


@app.route('/', methods=['GET'])
def index():
    bot.remove_webhook()
    bot.set_webhook(url='https://{}.herokuapp.com/{}'.format(APP_NAME, TELEGRAM_BOT_TOKEN))
    return 'Hello from Telegram Bot!', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
