const { Sensor } = require("./Sensor");
const { MQTTHandler } = require("../api/mqtt");

class SensorHandler {
  constructor() {
    this.sensors = [];
    this.mqttHandler = new MQTTHandler();
  }

  sensorConnected(id) {
    if (!this.idAlreadyPresent(id)) {
      this.sensors = this.sensors.concat(new Sensor(id));
    }
  }

  idAlreadyPresent(id) {
    return this.getSensorByID(id) != null;
  }

  /**
   *
   * @param {Any} id
   * @returns {Sensor}
   */
  getSensorByID(id) {
    let result = null;
    for (let i = 0; i < this.sensors.length && result == null; i++) {
      const sens = this.sensors[i];
      if (sens.id == id) {
        result = sens;
      }
    }
    return result;
  }

  readingReceived(sensorId, reading) {
    const sensor = this.getSensorByID(sensorId);
    if (sensor == null) {
      throw "Invalid id";
    }
    sensor.appendData(reading);
  }
}

module.exports = { SensorHandler, };
