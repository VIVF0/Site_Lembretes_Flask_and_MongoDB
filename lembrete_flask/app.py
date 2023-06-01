from flask import Flask
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'lembrete'

client=MongoClient('localhost',27017)
db=client.lembrete_mongodb

from views import *

if __name__ == '__main__':
    app.run(debug=True)