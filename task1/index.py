from flask import Flask, render_template, session, redirect, url_for, request
from forms import LoginForm
from models import Admin, Data
import os
from passlib.hash import sha256_crypt

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
