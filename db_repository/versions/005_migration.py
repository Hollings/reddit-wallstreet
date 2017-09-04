from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
portfolio = Table('portfolio', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('symbol', VARCHAR(length=64)),
    Column('subreddit_id', INTEGER),
    Column('amount', INTEGER),
)

portfolio = Table('portfolio', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('symbol', String(length=64)),
    Column('subreddit', Integer),
    Column('amount', Integer),
)

trades = Table('trades', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('symbol', VARCHAR(length=64)),
    Column('price', FLOAT),
    Column('timestamp', DATETIME),
    Column('subreddit_id', INTEGER),
)

trades = Table('trades', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('symbol', String(length=64)),
    Column('price', Float),
    Column('timestamp', DateTime),
    Column('subreddit', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['portfolio'].columns['subreddit_id'].drop()
    post_meta.tables['portfolio'].columns['subreddit'].create()
    pre_meta.tables['trades'].columns['subreddit_id'].drop()
    post_meta.tables['trades'].columns['subreddit'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['portfolio'].columns['subreddit_id'].create()
    post_meta.tables['portfolio'].columns['subreddit'].drop()
    pre_meta.tables['trades'].columns['subreddit_id'].create()
    post_meta.tables['trades'].columns['subreddit'].drop()
