const mqtt = require("mqtt");

class MQTTHandler {
  constructor(hostname, port) {
    this.client = mqtt.connect(`mqtt://${hostname}:${port}`);

    this.client.on("connect", () => {
      this.client.subscribe("/status/+");
      this.client.subscribe("/seism/+/raw");
      this.client.subscribe("/seism/+/events");
    });

    this.client.on("message", (topic, msg) => {
      this.handleMessage(topic, JSON.parse(msg.toString()));
    });

    this.onSensorOnlineCallback = () => {};
    this.onSensorOfflineCallback = () => {};
    this.onSensorReadingCallback = () => {};
    this.onSensorEventCallback = () => {};
  }

  handleMessage(topic, msg) {
    const levels = topic.split('/').slice(1);
    if (levels[0] == "status"){
      let status = msg['online'];
      let id = levels[1];
      if(status){
        this.onSensorOnlineCallback(id)
      }else{
        this.onSensorOfflineCallback(id);
      }
    }else if(levels[0] == "seism"){
      if(levels[2] == "raw"){
        let id = levels[1];
        this.onSensorReadingCallback(id, msg);
      }else if(levels[2] == "events"){
        let id = levels[1];
        this.onSensorEventCallback(id, msg);
      }
    }
  }


  setSensorOnlineCallback(fn){
    this.onSensorOnlineCallback = fn;
  }

  setSensorOfflineCallback(fn){
    this.onSensorOfflineCallback = fn;
  }

  setSensorReadingCallback(fn){
    this.onSensorReadingCallback = fn;
  }

  setOnSensorEventCallback(fn){
    this.onSensorEventCallback = fn;
  }

}

module.exports = {
  MQTTHandler,
};
