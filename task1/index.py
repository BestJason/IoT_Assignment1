from flask import Flask, render_template, session, redirect, url_for, request
from forms import LoginForm, CreateJobForm
from models import Admin, Data, Job
import os
from passlib.hash import sha256_crypt
import click

app = Flask(__name__)
app.secret_key = os.urandom(32)

def is_login():
    if 'username' in session:
        return True
    else:
        return False

@app.route('/')
def index():
    if is_login():
        return redirect(url_for('get_data'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        session['username'] = form.username.data
        return redirect(url_for('get_data'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/get_data')
def get_data():
    if is_login():
        res = Data.get_env_data()
        return render_template('data_view.html', res=res)
    else:
        return redirect(url_for('login'))

@app.route('/create_job', methods=['GET', 'POST'])
def create_job():
    if is_login():
        form = CreateJobForm(request.form)
        if request.method == 'POST' and form.validate():
            Job.write_job(form.command.data, form.frequency.data, form.comment.data)
            return redirect(url_for('get_jobs'))
        return render_template('job_create.html', form=form)
    else:
        return redirect(url_for('login'))

@app.route('/get_jobs')
def get_jobs():
    if is_login():
        jobs = Job.get_jobs()
        return render_template('jobs_view.html', res=jobs)
    else:
        return redirect(url_for('login'))

@app.route('/delete_job/comment/<string:comment>')
def delete_job(comment):
    if is_login():
        jobs = Job.get_jobs()
        jobs.remove_all(comment=comment)
        jobs.write()
        return redirect(url_for('get_jobs'))
    else:
        return redirect(url_for('login'))

@app.route('/init_admin_data')
def init_admin_data():
    if Admin.init_admin_data():
        return "Successfully Initialized!"
    return "Failed"

@app.route('/init_data_table')
def init_data_table():
    if Data.init_data_table():
        return "Successfully Initialized!"
    return "Failed"

@app.cli.command()
def get_insert_env_data():
    return Data.insert_env_data()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
