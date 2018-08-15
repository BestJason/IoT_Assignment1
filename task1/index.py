from flask import Flask, render_template, session, redirect, url_for, request
from forms import LoginForm
from models import Admin
import os
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.secret_key = os.urandom(32)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('get_data'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        return redirect(url_for('get_data'))
    return render_template('login.html', form=form)

@app.route('/get_data')
def get_data():
    return "data"

@app.route('/init_admin_data')
def init_admin_data():
    if Admin.init_admin_data():
        return "Successfully Initialized!"
    return "Failed"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
