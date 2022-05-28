class Sensor {
  constructor(id) {
    this.id = id;
    this.readings = [];
    this.online = true;
    this.events = [];

    let now = Date.now();

    this.timestamps = this.readings.map((_, i) => {
      return new Date(now + i * 1000);
    });
    this.timestampsToString = this.timestamps.map((ts) => ts.toLocaleTimeString());
  }

  appendData(data, timestamps) {
    this.readings = this.readings.concat(data);
    this.timestamps = this.timestamps.concat(timestamps);
    if (timestamps instanceof Array) {
      this.timestampsToString = this.timestampsToString.concat(
        timestamps.map((ts) => ts.toLocaleTimeString())
      );
    } else {
      this.timestampsToString = this.timestampsToString.concat(
        timestamps.toLocaleTimeString()
      );
    }
    if (this.readings.length > 1000) {
      this.readings = this.readings.slice(this.readings.length - 100);
      this.timestamps = this.timestamps.slice(this.timestamps.length - 100);
      this.timestampsToString = this.timestampsToString.slice(
        this.timestampsToString.length - 100
      );
    }
  }

  appendEvent(ev) {
    this.events = this.events.concat(ev);
    this.events.sort((a, b) => a.datetime - b.datetime);
  }

  getData() {
    return this.readings;
  }

  getTimestamps() {
    return this.timestamps;
  }

  setOnline(o) {
    this.online = o;
  }

  isOnline() {
    return this.online;
  }
}

module.exports = {
  Sensor,
};
