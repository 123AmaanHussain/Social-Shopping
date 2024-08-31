from flask import Flask
from flask_pymongo import PyMongo
import os

app = Flask(__name__)

# Set a secret key for session encryption
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # You can replace 'your_secret_key' with a stronger secret key

# MongoDB Configuration
app.config.from_object('app.config.Config')

mongo = PyMongo(app)

from app import routes
