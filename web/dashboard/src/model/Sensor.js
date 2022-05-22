class Sensor {
  constructor(id) {
    this.id = id;
    this.readings = [1, 2, 3, 4, 1, 2, 3, 4];
    let now = Date.now();

    this.timestamps = this.readings.map((_, i) => {
      return new Date(now + i * 1000);
    });
  }

  appendData(data, timestamps) {
    this.readings = this.readings.concat(data);
    this.timestamps = this.timestamps.concat(timestamps);
  }

  getData() {
    return this.readings;
  }

  getTimestamps() {
    return this.timestamps;
  }
}

module.exports = {
  Sensor,
};
