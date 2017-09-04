from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
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
    post_meta.tables['trades'].columns['buyOrSell'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['trades'].columns['buyOrSell'].drop()
