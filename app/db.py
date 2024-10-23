from app import app
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os


load_dotenv()  # take environment variables from .env.

# Mysql Settings

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'Matthews'
app.config['MYSQL_PASSWORD'] = 'MAtt1233xd'
app.config['MYSQL_DB'] = 'flaskcontact'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# MySQL Connection
mysql = MySQL(app)
