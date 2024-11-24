from flask import Flask
from flask_mysqldb import MySQL
from urllib.parse import quote_plus
import mysql.connector

# Initialize the Flask app
app = Flask(__name__)
app.secret_key='your_secret_key'

# Setup MySQL database connection string
username = quote_plus("your_username")
password = quote_plus("your_password")

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = username
app.config['MYSQL_PASSWORD'] = password
app.config['MYSQL_DB'] = 'database'

db=MySQL(app)

