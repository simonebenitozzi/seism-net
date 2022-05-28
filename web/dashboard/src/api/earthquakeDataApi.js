class EarthquakeDataApi {
  constructor(host, port) {
    this.baseUrl = `http://${host}:${port}/`;
  }

  async getPastEvents(sensorID, count) {
    count = count || 10;
    let reqData = {
      count: count,
    };
    const reqURL = this.baseUrl + `seismograph/${sensorID}/events?limit=${count}`;
    const responseData = await this.makeJsonGETRequest(reqURL, reqData);
    return await responseData.json()
  }

  async makeJsonGETRequest(url) {
    return await fetch(url, {
      method: "GET",
    });
  }
}

export {
  EarthquakeDataApi
}