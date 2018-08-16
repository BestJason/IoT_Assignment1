import sqlite3
from flask import g
from passlib.hash import sha256_crypt

DATABASE = './db/database.db'

ADMIN_TABLE_NAME = 'iot_admin'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'IoTadmin123'

DATA_TABLE_NAME = 'iot_data'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    res = cur.fetchall()
    cur.close()
    return (res[0] if res else None) if one else res

class Data():
    def init_data_table():
        try:
            cur = get_db().cursor()
            cur.execute("DROP TABLE IF EXISTS {}". format(DATA_TABLE_NAME))
            cur.execute("CREATE TABLE {} (humidity DOUBLE(30, 8) NOT NULL, temperature DOUBLE(30, 8) NOT NULL, pressure DOUBLE(30, 8) NOT NULL, created_at DATETIME)". format(DATA_TABLE_NAME))
            return True
        except:
            return False

class Admin():
    def init_admin_data():
        try:
            cur = get_db().cursor()
            cur.execute("DROP TABLE IF EXISTS {}". format(ADMIN_TABLE_NAME))
            cur.execute("CREATE TABLE {}(username VARCHAR(255), password CHAR(128))". format(ADMIN_TABLE_NAME))
            password = sha256_crypt.encrypt(ADMIN_PASSWORD)
            cur.execute("INSERT INTO {} VALUES(?, ?)". format(ADMIN_TABLE_NAME), (ADMIN_USERNAME, password))
            get_db().commit()
            return True
        except ValueError as e:
            return False
    
    def is_admin(username, password):
        try:
            cur = get_db().cursor()
            sql = "SELECT * FROM {} WHERE username = ?". format(ADMIN_TABLE_NAME)
            res = query_db(sql, [username], one=True)
            if res is not None and sha256_crypt.verify(password, res[1]):
                return True
            return False
        except ValueError as e:
            return False






