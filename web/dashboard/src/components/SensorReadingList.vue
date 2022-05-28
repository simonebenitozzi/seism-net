<template>
  <div class="md-layout" id="root">
    <div
      class="md-layout-item md-size-33 sensor-reading-container"
      v-for="sensor in sensors"
      :key="sensor.id"
    >
      <md-card class="sensor-reading-col">
        <SensorReadingsVisualizer
          id="readings-chart"
          :datapoints="sensor.getData()"
          :displayLimit="50"
          :labels="sensor.timestampsToString"
          :datasetName="sensor.id"
          :chartHeight="150"
          :chartWidth="300"
          :sensorOnline="sensor.online"
        />
        <md-divider></md-divider>
        <div id="table-container">
          <SeismicEventsVisualizer
            v-if="sensor.events.length > 0"
            :events="sensor.events.map(ev =>  {
              return{
                timestamp: ev.timestamp.toISOString(),
                frequency: ev.frequency,
                magnitude: ev.magnitude,
                mercalli: ev.mercalli,

              }
            })"
          />
          <md-empty-state
            v-else
            md-label="No notable seismic data available"
            md-icon="timeline"
          ></md-empty-state>
        </div>
      </md-card>
      <!-- <div class="md-layout-item md-size-60 sensor-reading-col">
      </div> -->
    </div>
  </div>
</template>

<script>
import SensorReadingsVisualizer from "./SensorReadingsVisualizer.vue";
import { SensorHandler } from "../model/SensorHandler";
import SeismicEventsVisualizer from "./SeismicEventsVisualizer.vue";

export default {
  name: "SensorReadingList",

  components: {
    SensorReadingsVisualizer,
    SeismicEventsVisualizer,
  },

  data() {
    return {
      sensorHandler: new SensorHandler(),
    };
  },

  methods: {
    addData() {
      this.sensors[0].appendData(6, new Date(Date.now()));
    },
  },

  computed: {
    sensors() {
      return this.sensorHandler.sensors;
    },
  },
};
</script>

<style scoped>
.sensor-reading-container {
  margin-bottom: 0.5rem !important;
  height: 25rem;
  max-height: 29.5rem;
}

.sensor-reading-col {
  max-height: inherit;
  height: inherit;
  display: flex;
  flex-direction: column;
}

#table-container {
  flex-grow: 1;

}

#readings-chart{
  flex-grow: 0;
  flex-shrink: 0;
}
</style>