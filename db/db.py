from lib2to3.pytree import Base
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    Table,
    create_engine)
from sqlalchemy import MetaData

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

conn_string = "sqlite:///" + os.path.join(BASE_DIR, 'tracks.db')

engine = create_engine(conn_string, echo=True)

meta = MetaData()

tracks = Table('tracks', meta,
    Column('id', Integer, primary_key=True),
    Column('artist_name',String(64), nullable=False, unique=False),
    Column('track_name',String(64), nullable=False, unique=False),
    Column('cluster',Integer, nullable=False, unique=False),
    Column('energy',Float, nullable=False, unique=False),
    Column('valence',Float, nullable=False, unique=False),
    Column('acousticness',Float, nullable=False, unique=False),
    Column('liveness',Float, nullable=False, unique=False)
)

meta.create_all(engine)

