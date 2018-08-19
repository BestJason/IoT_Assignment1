# import necessary packages
import sqlite3
from flask import g
from passlib.hash import sha256_crypt
from sense_hat import SenseHat
from crontab import CronTab
import requests
import time
import json
import bluetooth

# define database address
DATABASE = '../db/database.db'

# define admin table name
ADMIN_TABLE_NAME = 'iot_admin'

# define admin username
ADMIN_USERNAME = 'admin'

# define admin password
ADMIN_PASSWORD = 'IoTadmin123'

# define data table name
DATA_TABLE_NAME = 'iot_data'

# define alarm table name
ALARM_TABLE_NAME = 'iot_alarm'

# define PushBullet API Access_token and API Address
ACCESS_TOKEN = 'o.HA05DAZtj2DqlDvHpCLu3CPDCWqKsbF5'
API_ADDRESS = 'https://api.pushbullet.com/v2/pushes'

# command function for connecting sqlite
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# common function for closing sqlite
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# common function for running query
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    res = cur.fetchall()
    cur.close()
    return (res[0] if res else None) if one else res

# Bluetooth Model
class BlueTooth():
    # get bluetooth devices
    def get_bluetooth():
        devices = bluetooth.discover_devices(lookup_names = True)
        return devices

    # greet by bluetooth
    def greet(name, addr):
        device_name = bluetooth.lookup_name(addr, timeout = 5)
        if device_name == name:
            print("Hi {}! Your device ({}) has the MAC address: {}". format(name, name, addr))
            sense = SenseHat()
            temp = sense.get_temperature()
            temp = round(temp, 2)
            sense.show_message("Hi {}! Current Temp is {}*c". format(name, temp), scroll_speed=0.05)
            return True
        else:
            return False

# Alarm Model
class Alarm():
    # init table
    def init_alarm_table():
        try:
            cur = get_db().cursor()
            cur.execute("DROP TABLE IF EXISTS {}". format(ALARM_TABLE_NAME))
            cur.execute("CREATE TABLE {} (threshold_key VARCHAR(255) NOT NULL, threshold_opt VARCHAR(32) NOT NULL, threshold_val DOUBLE(30, 8) NOT NULL, created_at DATETIME)". format(ALARM_TABLE_NAME))
            return True
        except ValueError:
            return False

    # insert alarm
    def insert_alarm_threshold(threshold_key, threshold_opt, threshold_val):
        try:
            cur = get_db().cursor()
            cur.execute("INSERT INTO {} VALUES(?, ?, ?, datetime(CURRENT_TIMESTAMP,'localtime'))". format(ALARM_TABLE_NAME), (threshold_key, threshold_opt, threshold_val))
            get_db().commit()
            return True
        except ValueError:
            return False

    # get alatm list
    def get_alarms():
        sql = "SELECT rowid, threshold_key, threshold_opt, threshold_val, created_at FROM {}". format(ALARM_TABLE_NAME)
        res = query_db(sql)
        return res

    # delete alarm data
    def delete_alarm(id):
        try:
            cur = get_db().cursor()
            sql = "DELETE FROM {} WHERE rowid = ?". format(ALARM_TABLE_NAME)
            cur.execute(sql, [id])
            get_db().commit()
            return True
        except:
            return False

    # check if alarms are triggered
    def is_alarm(row, value):
        if row[2] == '<':
            return row[3] > value
        elif row[2] == '=':
            return row[3] == value
        elif row[2] == '>':
            return row[3] < value
        else:
            return False

    # enable alarm listen
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

    # send alarm to device
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

# Environment Data Model
class Data():
    # init table
    def init_data_table():
        try:
            cur = get_db().cursor()
            cur.execute("DROP TABLE IF EXISTS {}". format(DATA_TABLE_NAME))
            cur.execute("CREATE TABLE {} (humidity DOUBLE(30, 8) NOT NULL, temperature DOUBLE(30, 8) NOT NULL, pressure DOUBLE(30, 8) NOT NULL, created_at DATETIME)". format(DATA_TABLE_NAME))
            return True
        except ValueError:
            return False

    # insert environment data
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

    # get environment data list
    def get_env_data():
        sql = "SELECT rowid, humidity, temperature, pressure, created_at FROM {}". format(DATA_TABLE_NAME)
        res = query_db(sql)
        return res

    # get humidity
    def get_humidity():
        sql = "SELECT humidity, created_at FROM {}". format(DATA_TABLE_NAME)
        res = query_db(sql)
        return res

    # get temperature data
    def get_temperature():
        sql = "SELECT temperature, created_at FROM {}". format(DATA_TABLE_NAME)
        res = query_db(sql)
        return res

    # get pressure data
    def get_pressure():
        sql = "SELECT pressure, created_at FROM {}". format(DATA_TABLE_NAME)
        res = query_db(sql)
        return res

# Job Model
class Job():
    # write a job into cron
    def write_job(command, expression='* * * * *', comment=''):
        cron = CronTab(user='pi')
        job  = cron.new(command=command, comment=comment)
        job.setall(expression)
        cron.write()

    # get cron job list
    def get_jobs():
        cron = CronTab(user='pi')
        return cron

# Admin Model
class Admin():
    # init table
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

    # check if user is admin
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






