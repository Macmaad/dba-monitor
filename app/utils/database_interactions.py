import sqlite3

from utils.app_utils import logger


def execute_query(query, params=()):
    response = []
    db_connection = sqlite3.connect("app_db.db")
    cursor_ = db_connection.cursor()
    try:
        cursor_.execute(query, params)
        response = cursor_.fetchall()
    except Exception as e:
        logger.error(e)
    finally:
        db_connection.commit()
        db_connection.close()
    return response
