import sqlite3
from flask import g
from passlib.hash import sha256_crypt
from sense_hat import SenseHat
from crontab import CronTab
import requests
import time
import json

DATABASE = '../db/database.db'

ADMIN_TABLE_NAME = 'iot_admin'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'IoTadmin123'

DATA_TABLE_NAME = 'iot_data'

ALARM_TABLE_NAME = 'iot_alarm'

ACCESS_TOKEN = 'o.HA05DAZtj2DqlDvHpCLu3CPDCWqKsbF5'
API_ADDRESS = 'https://api.pushbullet.com/v2/pushes'

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

class Alarm():
    def init_alarm_table():
        try:
            cur = get_db().cursor()
            cur.execute("DROP TABLE IF EXISTS {}". format(ALARM_TABLE_NAME))
            cur.execute("CREATE TABLE {} (threshold_key VARCHAR(255) NOT NULL, threshold_opt VARCHAR(32) NOT NULL, threshold_val DOUBLE(30, 8) NOT NULL, created_at DATETIME)". format(ALARM_TABLE_NAME))
            return True
        except ValueError:
            return False

    def insert_alarm_threshold(threshold_key, threshold_opt, threshold_val):
        try:
            cur = get_db().cursor()
            cur.execute("INSERT INTO {} VALUES(?, ?, ?, datetime(CURRENT_TIMESTAMP,'localtime'))". format(ALARM_TABLE_NAME), (threshold_key, threshold_opt, threshold_val))
            get_db().commit()
            return True
        except ValueError:
            return False

    def get_alarms():
        sql = "SELECT rowid, threshold_key, threshold_opt, threshold_val, created_at FROM {}". format(ALARM_TABLE_NAME)
        res = query_db(sql)
        return res

    def delete_alarm(id):
        try:
            cur = get_db().cursor()
            sql = "DELETE FROM {} WHERE rowid = ?". format(ALARM_TABLE_NAME)
            cur.execute(sql, [id])
            get_db().commit()
            return True
        except:
            return False

    def is_alarm(row, value):
        if row[2] == '<':
            return row[3] > value
        elif row[2] == '=':
            return row[3] == value
        elif row[2] == '>':
            return row[3] < value
        else:
            return False

    def enable_alarm():
        try:
            while True:
                print("Start to listen.....")
                alarms = Alarm.get_alarms()
                print("Got Alarms: {}". format(alarms))
                for row in alarms:
                    if row[1] == 'humidity':
                        value = SenseHat().get_humidity()
                    elif row[1] == 'temperature':
                        value = SenseHat().get_temperature()
                    elif row[1] == 'pressure':
                        value = SenseHat().get_pressure()
                    if Alarm.is_alarm(row, value):
                        print("Alarm Condition is met!!!")
                        Alarm.send_alarm('Alarm Message!!!', '{} met the demand of alarming: {} {} {} -- current {} : {}'. format(row[1], row[1], row[2], row[3], row[1], value))
                        print("{} Alarmed!!!". format(row[1]))
                time.sleep(30)
                print("Continue to listen....")
        except Exception as e:
            print(e)
            return False

    def send_alarm(title, body):
        request = {
            "type": "note",
            "title": title,
            "body": body
        }
        headers = {
            'Authorization': 'Bearer ' + ACCESS_TOKEN,
            'Content-Type': 'application/json'
        }
        res = requests.post(API_ADDRESS, data = json.dumps(request), headers = headers)
        if res.status_code != 200:
            raise Exception(res.raise_for_status())
        else:
            print('complete sending')

class Data():
    def init_data_table():
        try:
            cur = get_db().cursor()
            cur.execute("DROP TABLE IF EXISTS {}". format(DATA_TABLE_NAME))
            cur.execute("CREATE TABLE {} (humidity DOUBLE(30, 8) NOT NULL, temperature DOUBLE(30, 8) NOT NULL, pressure DOUBLE(30, 8) NOT NULL, created_at DATETIME)". format(DATA_TABLE_NAME))
            return True
        except ValueError:
            return False

    def insert_env_data():
        try:
            cur = get_db().cursor()
            humidity = SenseHat().get_humidity()
            temperature = SenseHat().get_temperature()
            pressure = SenseHat().get_pressure()
            cur.execute("INSERT INTO {} VALUES(?, ?, ?, datetime(CURRENT_TIMESTAMP,'localtime'))". format(DATA_TABLE_NAME), (humidity, temperature, pressure))
            get_db().commit()
            return True
        except ValueError:
            return False

    def get_env_data():
        sql = "SELECT rowid, humidity, temperature, pressure, created_at FROM {}". format(DATA_TABLE_NAME)
        res = query_db(sql)
        return res

    def get_humidity():
        sql = "SELECT humidity, created_at FROM {}". format(DATA_TABLE_NAME)
        res = query_db(sql)
        return res

    def get_temperature():
        sql = "SELECT temperature, created_at FROM {}". format(DATA_TABLE_NAME)
        res = query_db(sql)
        return res

    def get_pressure():
        sql = "SELECT pressure, created_at FROM {}". format(DATA_TABLE_NAME)
        res = query_db(sql)
        return res

class Job():
    def write_job(command, expression='* * * * *', comment=''):
        cron = CronTab(user='pi')
        job  = cron.new(command=command, comment=comment)
        job.setall(expression)
        cron.write()

    def get_jobs():
        cron = CronTab(user='pi')
        return cron


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






