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
def create_table():
    Base.metadata.create_all(engine)

class User(Base):
    __tablename__ = 'User'
    profile = sq.Column(sq.Integer, primary_key=True)
    like = sq.Column(sq.Boolean)

# def add_main(id):
#     session = Session(bind=engine)
#     create_table()
#     element = User(user_id=id)
#     session.add(element)
#     #session.add_all(element)
#     session.commit()
#     session.close()

def add_toDB(like, profile):
    try:
        session = Session(bind=engine)
        create_table()
        element = User(profile=profile)
        session.add(element)
        #session.add_all(element)
        session.commit()
        session.close()
        setvalue(profile, like)
    except:
        return False

def setvalue(id, like):
    session = Session(bind=engine)
    if like=="like":
        session.query(User).filter(User.profile == id).update({'like': True})
    else:
        session.query(User).filter(User.profile == id).update({'like': False})
    session.commit()
    session.close()

def consult_db():
    result_list = []
    session = Session(bind=engine)
    query = session.query(User).all()
    for id in query:
        result_list.append(id.profile)
    session.commit()
    session.close()
    return result_list
