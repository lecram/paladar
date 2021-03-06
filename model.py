# http://peewee.readthedocs.org/en/latest/index.html

import json

import pymysql

from peewee import *

IntegrityError = pymysql.err.IntegrityError

f = open("dbauth.json", "r")
dbauth = json.load(f)
f.close()

paladar_db = MySQLDatabase("paladar", **dbauth)

class PaladarModel(Model):
    class Meta:
        database = paladar_db

class User(PaladarModel):
    handle = CharField(unique=True)
    name = CharField()
    email = CharField()
    language = CharField(default="en")
    timezone = CharField(default="UTC")
    hashed_password = CharField()
    corpuslen = BigIntegerField(default=0)

class ChannelType(PaladarModel):
    name = CharField(unique=True)

class Channel(PaladarModel):
    url = CharField(unique=True)
    type_ = ForeignKeyField(ChannelType, related_name='channels')
    title = CharField()
    description = TextField()

class Entry(PaladarModel):
    url = CharField(unique=True)
    channel = ForeignKeyField(Channel, related_name='entries')
    pubtime = DateTimeField()
    title = CharField()
    summary = TextField()

    class Meta:
        order_by = ('-pubtime',)

class Subscription(PaladarModel):
    user = ForeignKeyField(User, related_name='subscriptions')
    channel = ForeignKeyField(Channel, related_name='subscriptions')

    class Meta:
        indexes = ((('user', 'channel'), True),)

class Rating(PaladarModel):
    user = ForeignKeyField(User, related_name='ratings')
    entry = ForeignKeyField(Entry, related_name='ratings')
    rate = IntegerField()

class Word(PaladarModel):
    spelling = CharField(unique=True)

class Score(PaladarModel):
    user = ForeignKeyField(User, related_name='scores')
    word = ForeignKeyField(Word, related_name='scores')
    numnum = IntegerField()
    numden = IntegerField()
    dennum = IntegerField()
    denden = IntegerField()

def create_tables():
    tables = [
      User, ChannelType, Channel, Entry,
      Subscription, Rating, Word, Score
    ]
    for table in tables:
        table.create_table()

if __name__ == "__main__":
    create_tables()
