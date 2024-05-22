from peewee import *

db = SqliteDatabase("nexus.db")

class Channel(Model):
    server_id = IntegerField()
    channel_id = IntegerField()

    class Meta:
        database = db

db.connect()
db.create_tables([Channel])
