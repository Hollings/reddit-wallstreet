from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
history = Table('history', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('symbol', VARCHAR(length=64)),
    Column('price', FLOAT),
    Column('subreddit_id', INTEGER),
    Column('timestamp', DATETIME),
)

trades = Table('trades', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('symbol', String(length=64)),
    Column('price', Float),
    Column('timestamp', DateTime),
    Column('subreddit_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['history'].drop()
    post_meta.tables['trades'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['history'].create()
    post_meta.tables['trades'].drop()
