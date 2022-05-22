const mqtt = require("mqtt"); // require mqt

class MQTTHandler {
  constructor() {
    this.client = mqtt.connect("mqtt://localhost:9001");

    this.client.on("connect", () => {
      this.client.subscribe("seism/+/raw");
    });

    this.client.on("message", (topic, msg) => {
      this.handleMessage(topic, msg);
    });
  }

  handleMessage(topic, msg) {
    console.log(`@${topic} : ${msg.toString()}`);
  }
}

module.exports = {
  MQTTHandler,
};
