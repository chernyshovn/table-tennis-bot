import os
import flask
from flask import redirect
from flask_simplelogin import SimpleLogin, login_required, url_for
from telebot import types
from app import app
from bot_handlers import bot
from database.database import db
import config

app.config['SECRET_KEY'] = config.APP_SECRET

app.config['SIMPLELOGIN_USERNAME'] = config.ADMIN_USERNAME
app.config['SIMPLELOGIN_PASSWORD'] = config.ADMIN_PASSWORD
SimpleLogin(app)

app.config['SQLALCHEMY_DATABASE_URI'] = config.DB_CONNECTION_STRING
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


@app.route('/' + config.TELEGRAM_BOT_TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates([types.Update.de_json(flask.request.stream.read().decode('utf-8'))])
    return '!', 200


@app.route('/', methods=['GET'])
@login_required
def index():
    bot.remove_webhook()
    bot.set_webhook(url='https://{}.herokuapp.com/{}'.format(config.APP_NAME, config.TELEGRAM_BOT_TOKEN))
    return redirect(url_for('statistics_all_matches'))


@app.route('/statistics', methods=['GET'])
@login_required
def statistics():
    return redirect(url_for('statistics_all_matches'))


@app.route('/statistics/all-matches', methods=['GET'])
@login_required
def statistics_all_matches():
    return flask.render_template('all_matches.html')


@app.route('/statistics/comparison', methods=['GET'])
@login_required
def statistics_comparison():
    return flask.render_template('comparison.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
