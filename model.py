# http://peewee.readthedocs.org/en/latest/index.html

from peewee import *

paladar_db = SqliteDatabase("paladar.db")

class PaladarModel(Model):
    class Meta:
        database = paladar_db

class User(PaladarModel):
    handle = CharField()
    name = CharField()
    corpuslen = BigIntegerField()

class ChannelType(PaladarModel):
    handle = CharField()

class Channel(PaladarModel):
    url = CharField()
    type_ = ForeignKeyField(ChannelType, related_name='channels')
    title = CharField()
    description = TextField()

class Entry(PaladarModel):
    url = CharField()
    channel = ForeignKeyField(Channel, related_name='entries')
    pubtime = DateTimeField()
    title = CharField()
    summary = TextField()

class Subscription(PaladarModel):
    user = ForeignKeyField(User, related_name='subscriptions')
    channel = ForeignKeyField(Channel, related_name='subscriptions')

class Rating(PaladarModel):
    user = ForeignKeyField(User, related_name='ratings')
    entry = ForeignKeyField(Entry, related_name='ratings')
    rate = IntegerField()

class Word(PaladarModel):
    spelling = CharField()

class Score(PaladarModel):
    user = ForeignKeyField(User, related_name='scores')
    word = ForeignKeyField(Word, related_name='scores')
    numnum = IntegerField()
    numden = IntegerField()
    dennum = IntegerField()
    denden = IntegerField()

if __name__ == "__main__":
    tables = [
      User, ChannelType, Channel, Entry,
      Subscription, Rating, Word, Score
    ]
    for table in tables:
        table.create_table()
