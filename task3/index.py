# import necessary packages
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from forms import LoginForm, CreateJobForm, SetAlarmForm
from models import Admin, Data, Job, Alarm, BlueTooth
import os
from passlib.hash import sha256_crypt
import click
import json
import time

# Initialize framework
app = Flask(__name__)

# create secret key for form to avoid CSRF attack
app.secret_key = os.urandom(32)

# common function for check id user signs in
def is_login():
    if 'username' in session:
        return True
    else:
        return False

# before requesting, check if user signs in
@app.before_request
def check_login():
    if request.path == '/login' or request.path == '/init_admin_data':
        return None
    if not is_login():
        return redirect(url_for('login'))

# index page
@app.route('/')
def index():
    return redirect(url_for('get_data'))

# login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        session['username'] = form.username.data
        return redirect(url_for('get_data'))
    return render_template('login.html', form=form)

# log out page
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# get environment data page
@app.route('/get_data')
def get_data():
    res = Data.get_env_data()
    return render_template('data_view.html', res=res)

# get humidity chart page
@app.route('/get_humidity')
def get_humidity():
    res = json.dumps(Data.get_humidity())
    return render_template('chart_view.html', res=res, title="Humidity", unit=" rH")

# get temperature chart page
@app.route('/get_temperature')
def get_temperature():
    res = json.dumps(Data.get_temperature())
    return render_template('chart_view.html', res=res, title="Temperature", unit=" C")

# get pressure chart page
@app.route('/get_pressure')
def get_pressure():
    res = json.dumps(Data.get_pressure())
    return render_template('chart_view.html', res=res, title="Pressure", unit="Millibars")

# create cron job page
@app.route('/create_job', methods=['GET', 'POST'])
def create_job():
    form = CreateJobForm(request.form)
    if request.method == 'POST' and form.validate():
        Job.write_job(form.command.data, form.frequency.data, form.comment.data)
        return redirect(url_for('get_jobs'))
    return render_template('job_create.html', form=form)

# get cron job list page
@app.route('/get_jobs')
def get_jobs():
    jobs = Job.get_jobs()
    return render_template('jobs_view.html', res=jobs)

# delete job link
@app.route('/delete_job/comment/<string:comment>')
def delete_job(comment):
    jobs = Job.get_jobs()
    jobs.remove_all(comment=comment)
    jobs.write()
    return redirect(url_for('get_jobs'))

# create alarm page
@app.route('/set_alarm_threshold', methods=['GET', 'POST'])
def set_alarm_threshold():
    form = SetAlarmForm(request.form)
    if request.method == 'POST' and form.validate():
        if Alarm.insert_alarm_threshold(form.threshold_key.data, form.threshold_opt.data, form.threshold_val.data):
            return redirect(url_for('get_alarms'))
    return render_template('set_alarm_threshold.html', form=form)

# get alarms list page
@app.route('/get_alarms')
def get_alarms():
    alarms = Alarm.get_alarms()
    return render_template('alarms_view.html', res=alarms)

# delete alarm link
@app.route('/delete_alarm/id/<int:id>')
def delete_alarm(id):
    Alarm.delete_alarm(id)
    return redirect(url_for('get_alarms'))

# get devices list
@app.route('/get_devices')
def get_devices():
    return render_template('bluetooth_view.html')

# get devices list by json format
@app.route('/get_devices_json')
def get_devices_json():
    blues = BlueTooth.get_bluetooth()
    return json.dumps(blues)

# greet device
@app.route('/bluetooth_greet', methods=['POST'])
def greet():
    name = request.form.get("name")
    addr = request.form.get("addr")
    if BlueTooth.greet(name, addr):
      return json.dumps({'code': 1, 'msg': 'ok'})
    return json.dumps({'code': -1, 'msg': 'fail'})

# initlialize the admin table data
@app.route('/init_admin_data')
def init_admin_data():
    if Admin.init_admin_data():
        return "Successfully Initialized!"
    return "Failed"

# initlialize the environment data table data
@app.route('/init_data_table')
def init_data_table():
    if Data.init_data_table():
        return "Successfully Initialized!"
    return "Failed"

# initlialize the alarm table data
@app.route('/init_alarm_table')
def init_alarm_table():
    if Alarm.init_alarm_table():
        return "Successfully Initialized!"
    return "Failed"

# create command line to collect environment data
@app.cli.command()
def get_insert_env_data():
    return Data.insert_env_data()

# create command line to listen alarm
@app.cli.command()
def enable_alarm():
    return Alarm.enable_alarm()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
