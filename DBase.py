from sqlalchemy.orm import declarative_base, relationship
import sqlalchemy as sq
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker

# подключаем базу данных
db = f'postgresql://postgres:300592@localhost:5432/vkinder'
engine = sq.create_engine(db)
Session = sessionmaker()
if not database_exists(engine.url):
    create_database(engine.url)
    print('База данных создана...')

Base = declarative_base()

class User(Base):
    __tablename__ = 'User'
    user_id = sq.Column(sq.Integer, primary_key = True)
    white = relationship('White', backref='User')
    black = relationship('Black', backref='User')

class White(Base):
    __tablename__ = 'White'
    profile = sq.Column(sq.Integer, primary_key = True)
    user_id = sq.Column(sq.Integer,sq.ForeignKey('User.user_id'))

class Black(Base):
    __tablename__ = 'Black'
    profile = sq.Column(sq.Integer, primary_key = True)
    user_id = sq.Column(sq.Integer,sq.ForeignKey('User.user_id'))



def add_main(id):
    session = Session(bind=engine)
    element = User(profile=id)
    session.add(element)
    session.add_all(element)
    session.commit()
    session.close()

def add_toDB(table, profile_id):
    session = Session(bind=engine)
    if table == 'black':
        element = Black(profile=profile_id)
        session.add(element)
        #session.add_all(element)
        session.commit()
        session.close()
    if table == 'white':
        element = White(profile=profile_id)
        session.add(element)
        #session.add_all(element)
        session.commit()
        session.close()

def consult_blacklist():
    session = Session(bind=engine)
    query = session.query(Black)
    print(str(query))
def consult_whitelist():
    session = Session(bind=engine)
    query = session.query(White)
    print(str(query))