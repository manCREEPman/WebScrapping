import sqlalchemy
from sqlalchemy import func
from sqlalchemy.orm import Session
import json


def createSession():

    tmp_dict = json.load(open('./privates.json', encoding='utf-8'))
    login = tmp_dict['bd_login']
    psw = tmp_dict['bd_psw']
    host = tmp_dict['bd_host']

    engine = sqlalchemy.create_engine(f"postgresql+psycopg2://{login}:{psw}@{host}/Papers")
    session = Session(bind=engine)

    return session


def insertInfo(info):
    session = createSession()

    sql = f"""Select pInsert('{info['title']}', '{info['author']}', '{info['annotation']}', '{info['url']}', '{info['paper_text']}'); """

    e = session.execute(sql)

    session.commit()
    session.close()

    return e.first()[0]

def getInfo(sql):

    session = createSession()

    e = session.execute(sql)
    session.close()

    return e.fetchall()