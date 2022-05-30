from wsgiref import headers
from flask import request, jsonify, Flask
import mysql.connector
import json
from datetime import datetime
import serial
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, resources={r"/*" : {'origins': "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

#serial_interface = serial.Serial('/dev/ttyUSB1', 115200)
configFile = open('config.json', 'r')

config = json.loads(configFile.read())

mydb = mysql.connector.connect(
  host=config['db_host'],
  user=config['db_user'],
  password=config['db_pass'],
  auth_plugin='mysql_native_password'
)


@app.route("/seismograph/<sensor_id>/events")
@cross_origin()
def earthquakes(sensor_id = 0):
    mydb.reconnect()
    args = request.args
    limit = args.get('limit', 20)
    cursor = mydb.cursor()
    cursor.execute(f"SELECT datetime, frequency, magnitude, mercalli FROM {config['db_name']}.earthquake_detection WHERE sensor_id = '{sensor_id}' ORDER BY datetime DESC LIMIT {limit}")
    rows = cursor.fetchall()
    result = []
    now = datetime.now()
    for r in rows:
        result.append({
            'datetime' : int(r[0].timestamp() * 1000),
            'frequency' : r[1],
            'magnitude' : r[2],
            'mercalli_scale' : r[3]
        })
    return jsonify(result)


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5000, debug=True)
