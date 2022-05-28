const { Sensor } = require("./Sensor");
const { MQTTHandler } = require("../api/mqtt");
import { EarthquakeDataApi } from "../api/earthquakeDataApi";

class SensorHandler {
  constructor() {
    this.sensors = [];

    this.earthquakeApi = new EarthquakeDataApi(
      process.env.VUE_APP_WEB_API_HOSTNAME,
      process.env.VUE_APP_WEB_API_PORT
    );
    this.mqttHandler = new MQTTHandler(
      process.env.VUE_APP_MQTT_HOSTNAME,
      process.env.VUE_APP_MQTT_PORT
    );
    this.mqttHandler.setSensorOnlineCallback((id) => {
      this.sensorConnected(id);
    });
    this.mqttHandler.setSensorOfflineCallback((id) => {
      this.sensorDisconnected(id);
    });
    this.mqttHandler.setSensorReadingCallback((id, read) => {
      this.readingReceived(id, read);
    });
    this.mqttHandler.setOnSensorEventCallback((id, ev) => {
      this.sensorEventReceived(id, ev);
    });
  }

  async sensorConnected(id) {
    console.log(`Sensor ${id} connected`);
    if (!this.idAlreadyPresent(id)) {
      console.log("Adding sensor");
      const newSensor = new Sensor(id);
      this.sensors = this.sensors.concat(newSensor);
      const pastReadings = await this.earthquakeApi.getPastEvents(
        newSensor.id,
        10
      );
      newSensor.appendEvent(pastReadings);
    } else {
      this.getSensorByID(id).setOnline(true);
    }
  }

  sensorDisconnected(id) {
    console.log(`Sensor offline ${id}`);
    const sens = this.getSensorByID(id);
    console.log(sens);
    if (sens) {
      sens.setOnline(false);
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
    if (sensor != null) {
      sensor.appendData(reading["reading_g"], new Date(Date.now()));
    }
  }

  sensorEventReceived(sensorId, event) {
    const sensor = this.getSensorByID(sensorId);
    if (sensor != null) {
      event["timestamp"] = new Date(Date.now());
      sensor.appendEvent(event);
    }
  }
}
export { SensorHandler };
