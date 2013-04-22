#coding: u8

import datetime

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Binary


import settings


now = lambda: datetime.datetime.now().strftime('%Y-%m:%d %H:%M:%S')
engine = sa.create_engine(
    'sqlite:///%s/data/cocoqq.db' % settings.APP_ROOT,
    encoding='utf8',
    echo=False,
)
db = orm.scoped_session(orm.sessionmaker(bind=engine))
Base = declarative_base()


class FriendHistory(Base):
    __tablename__ = 'friend_history'

    pk = Column(Integer, primary_key=True, autoincrement=True)
    to_uin = Column(Integer, index=True)
    friend_name = Column(String(20))
    from_uin = Column(Integer, index=True)
    content = Column(String)
    dt = Column(String, default=now, index=True)


class ImageStorage(Base):
    '''存放用户的离线图片'''
    __tablename__ = 'image_storage'

    pk = Column(Integer, primary_key=True, autoincrement=True)
    data = Column(Binary)


def init_db():
    metadata = Base.metadata
    metadata.create_all(engine)


if __name__ == '__main__':
    init_db()
