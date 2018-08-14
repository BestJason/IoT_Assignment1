from flask import Flask
import controllers.job_controller
import controllers.env_controller
import models.env_model

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True, host='192.168.0.12', port=8080)
