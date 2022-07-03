from database.database import db
from enums.telegram_user_state import TelegramUserState


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    telegram_id = db.Column(db.Integer, unique=True, nullable=True)


team_player = db.Table(
    'team_player',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), nullable=False),
    db.Column('player_id', db.Integer, db.ForeignKey('player.id'), nullable=False)
)


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=True)

    players = db.relationship('Player', secondary=team_player, lazy='subquery', backref=db.backref('teams', lazy=True))


tournament_team = db.Table(
    'tournament_team',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('tournament_id', db.Integer, db.ForeignKey('tournament.id'), nullable=False),
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), nullable=False)
)


tournament_match = db.Table(
    'tournament_match',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('tournament_id', db.Integer, db.ForeignKey('tournament.id'), nullable=False),
    db.Column('match_id', db.Integer, db.ForeignKey('match.id'), nullable=False)
)


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    initiator_telegram_user_id = db.Column(db.Integer, nullable=True)
    team_1_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    team_2_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    start_date_time = db.Column(db.DateTime, nullable=False)
    end_date_time = db.Column(db.DateTime, nullable=True)

    team_1 = db.relationship('Team', foreign_keys=[team_1_id], backref=db.backref('teams1', lazy=True))
    team_2 = db.relationship('Team', foreign_keys=[team_2_id], backref=db.backref('teams2', lazy=True))
    games = db.relationship('Game', backref='match', lazy=True)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    team_1_score = db.Column(db.Integer, nullable=False)
    team_2_score = db.Column(db.Integer, nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)


class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    initiator_telegram_user_id = db.Column(db.Integer, nullable=True)
    start_date_time = db.Column(db.DateTime, nullable=False)
    end_date_time = db.Column(db.DateTime, nullable=True)

    location = db.relationship('Location', backref=db.backref('tournaments', lazy=True))
    teams = db.relationship('Team', secondary=tournament_team, lazy='subquery', backref=db.backref('tournaments', lazy=True))
    matches = db.relationship('Match', secondary=tournament_match, lazy='subquery', backref=db.backref('tournaments', lazy=True))


class TelegramUserState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Enum(TelegramUserState), nullable=True)
