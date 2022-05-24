<template>
  <div class="md-layout">
    <div
      class="md-layout-item md-size-99 sensor-reading-container md-layout"
      v-for="sensor in sensors"
      :key="sensor.id"
    >
      <div class="md-layout-item md-size-40">
        <SensorReadingsVisualizer
          :datapoints="sensor.getData()"
          :displayLimit="50"
          :labels="
            sensor.getTimestamps().map((ts) => {
              return ts.toLocaleTimeString();
            })
          "
          :datasetName="sensor.id"
          :chartHeight="250"
          :chartWidth="300"
          :sensorOnline="sensor.online"
        />
      </div>
      <div class="md-layout-item md-size-60">
        <SeismicEventsVisualizer :events="sensor.events"/>
      </div>
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
  margin-bottom: 2rem;
}
</style>