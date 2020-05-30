from . import db
from flask_login import UserMixin
from sqlalchemy.orm import backref

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Tickets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_hash = db.Column(db.String(100), unique=True, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    raffle_id = db.Column(db.Integer, db.ForeignKey('raffles.id'))
    activated = db.Column(db.Boolean)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

class Members(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_name = db.Column(db.String(200), unique=True, nullable=False)
    member_link = db.Column(db.String(200), unique=True, nullable=False)
    member_tickets = db.relationship('Tickets', backref=backref("children", cascade="all,delete"), cascade="all,delete")

class Raffles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chance = db.Column(db.Integer, unique=False, nullable=False)
    date = db.Column(db.DateTime, unique=True, nullable=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    link = db.Column(db.String(200), unique=True, nullable=False)
    tickets = db.relationship('Tickets', backref=backref("children2", cascade="all,delete"), cascade="all,delete")
    description = db.Column(db.Text, nullable=True)
    winners = db.Column(db.Text, unique=False, nullable=True)
    ended = db.Column(db.Boolean)


