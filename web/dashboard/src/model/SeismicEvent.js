const SeismicEvent = function({timestamp, magnitude, frequency, mercalli}){
    this.timestamp = new Date(timestamp);
    this.magnitude = magnitude;
    this.frequency = frequency;
    this.mercalli = mercalli;
}

export{
    SeismicEvent
}