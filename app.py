from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
import sys

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
app.debug = True
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

if __name__ == '__main__':
    app.run()

from app import views, models