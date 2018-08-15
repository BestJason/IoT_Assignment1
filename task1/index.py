from flask import Flask, render_template, session, redirect, url_for
from forms import LoginForm
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('data'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', form=form)

@app.route('/data')
def getData():
    return "data"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
