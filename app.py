from flask import Flask, render_template, request, Response, json, jsonify
from routers.seatgeek import getSeatGeekData
from modules.event import Event
import routers.mongo as Database

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')

if __name__ == '__main__':
  app.run()