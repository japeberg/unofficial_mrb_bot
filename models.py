# data.py

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session


engine = create_engine('sqlite:///test.sqlite3', echo=True)






Base = declarative_base()


subscribed_lines = Table('subscribed_lines', Base.metadata,
    Column('chat_id', Integer, ForeignKey('subscriber.chat_id')),
    Column('line_id', Integer, ForeignKey('line.line_id'))
)

class subscriber(Base):
    __tablename__ = 'subscriber'

    chat_id = Column(Integer, primary_key=True)
    subscribed_on = Column(DateTime)
    lines = relationship("line",
                    secondary=subscribed_lines)

class line(Base):
    __tablename__ = 'line'

    line_id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)

class messages(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True)
    title = Column(String)
    text = Column(String)
    reason = Column(String)
    alternatives = Column(String)
    sent = Column(Boolean)
    read = Column(DateTime)
    line = ForeignKey('line.line_id')


Base.metadata.create_all(engine)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
