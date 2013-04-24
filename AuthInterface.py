## python modules
from storm.locals import *
from time import *


def getDBhandle():
    dbname = 'postgres://jytokmqhvhruvs:sEFZxUgkFc02iEogBgDJzuT2t4@ec2-23-21-209-205.compute-1.amazonaws.com:5432/ddetrgamclnu77'

    store = None
    while not store:
        try:
            database = create_database(dbname)
            store = Store(database)
        except Exception as e:
            print type(e), e.message
            pass
    return store


def getAccessLevel(token):
    db = getDBhandle()

    current_time = int(time())

    command = 'SELECT level FROM active_sessions ' \
            + 'WHERE token = ' + token + ' AND logout_time > ' + str(current_time)

    got_level = False
    while not got_level:
        try:
            results = db.execute(command)
            results = results.get_all()
            got_level = True
        except:
            pass
    if not results:
        return 0
    return results[0][0]


def updateSession(token, level, handles='', logout_time=900):
    db = getDBhandle()

    current_time = int(time())
    command = 'DELETE FROM active_sessions ' \
            + 'WHERE token = ' + token \
            + 'OR logout_time < ' + str(current_time)

    sessions_clear = False
    while not sessions_clear:
        try:
            db.execute(command)
            db.commit()
            sessions_clear = True
        except Exception as e:
            db.rollback()
            print type(e), e.message

    command = 'INSERT INTO active_sessions ' \
            + 'VALUES (' + ','.join([token, str(level), '\'' + handles + '\'', str(current_time + logout_time)]) + ')'
    session_loaded = False
    while not session_loaded:
        try:
            db.execute(command)
            db.commit()
            session_loaded = True
        except Exception as e:
            db.rollback()
            print type(e), e.message

    db.close()
