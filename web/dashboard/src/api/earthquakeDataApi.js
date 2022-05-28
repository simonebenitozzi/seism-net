import { SeismicEvent } from "../model/SeismicEvent";

class EarthquakeDataApi {
  constructor(host, port) {
    this.baseUrl = `http://${host}:${port}/`;
  }

  async getPastEvents(sensorID, count) {
    count = count || 10;
    let reqData = {
      count: count,
    };
    const reqURL =
      this.baseUrl + `seismograph/${sensorID}/events?limit=${count}`;
    const responseData = await this.makeJsonGETRequest(reqURL, reqData);
    const responseBody = await responseData.json();
    return responseBody.map(
      (ev) =>
        new SeismicEvent({
          timestamp: ev.datetime,
          magnitude: ev.magnitude,
          frequency: ev.frequency,
          mercalli: ev.mercalli_scale,
        })
    );
  }

  async makeJsonGETRequest(url) {
    return await fetch(url, {
      method: "GET",
    });
  }
}

export { EarthquakeDataApi };
