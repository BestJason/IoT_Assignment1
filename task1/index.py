from flask import Flask

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return 'index'

if __name__ == '__main__':
    app.run(debug=True, host='192.168.0.12', port=8080)
