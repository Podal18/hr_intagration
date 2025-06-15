import pymysql
from pymysql import cursors

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="diplom",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        port=3312
    )
def get_connection_for_auth():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="diplom",
        autocommit=True,
        port=3312
    )

