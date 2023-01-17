import sqlite3


def createConnectionCursor():
    sqlite_connection = sqlite3.connect('./db/data.db')
    cursor = sqlite_connection.cursor()
    return sqlite_connection, cursor


def insertInfo(info: dict):
    connection, cursor = createConnectionCursor()

    sql = f'select count(*) from papers where url = \'{info["url"]}\''

    cursor.execute(sql)
    count = cursor.fetchone()[0]
    if count == 0:
        sql = f'''
            insert into papers(title, author, annotation, paper_text, url, type) 
            values('{info["title"]}', '{info["author"]}', '{info["annotation"]}', '{info["paper_text"]}', '{info["url"]}', null)
        '''

        cursor.execute(sql)
        connection.commit()
    cursor.close()


def updateInfo(id: int, type: int):
    connection, cursor = createConnectionCursor()

    sql = f'update papers set type = {type} where id = {id}'

    cursor.execute(sql)
    connection.commit()
    cursor.close()


def getDBInfo(where_statement:str=''):
    connection, cursor = createConnectionCursor()

    sql = f'select id, paper_text, type from papers' + ' ' + where_statement # + ' limit 2'
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    return results


def setTypeNulls():
    connection, cursor = createConnectionCursor()

    sql = 'update papers set type = null'
    cursor.execute(sql)
    connection.commit()
    cursor.close()