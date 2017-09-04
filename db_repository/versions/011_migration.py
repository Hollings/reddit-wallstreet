from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
portfolio = Table('portfolio', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('symbol', String(length=64)),
    Column('subreddit', Integer),
    Column('amount', Integer),
)

price = Table('price', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('symbol', String(length=64)),
    Column('price', Float),
    Column('lastUpdated', DateTime),
)

subreddit = Table('subreddit', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=64)),
    Column('money', Integer),
)

trades = Table('trades', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('symbol', String(length=64)),
    Column('permalink', String(length=64)),
    Column('buyOrSell', String(length=64)),
    Column('price', Float),
    Column('timestamp', DateTime),
    Column('subreddit', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['portfolio'].create()
    post_meta.tables['price'].create()
    post_meta.tables['subreddit'].create()
    post_meta.tables['trades'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['portfolio'].drop()
    post_meta.tables['price'].drop()
    post_meta.tables['subreddit'].drop()
    post_meta.tables['trades'].drop()
