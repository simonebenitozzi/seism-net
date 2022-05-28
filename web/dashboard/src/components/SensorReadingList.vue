<template>
  <div class="md-layout" id="root">
    <div
      class="md-layout-item md-size-100 sensor-reading-container md-layout"
      v-for="sensor in sensors"
      :key="sensor.id"
    >
      <div class="md-layout-item md-size-40 sensor-reading-col">
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
      <div class="md-layout-item md-size-60 sensor-reading-col">
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
  margin-bottom: 5rem !important;
  height: 25rem;
  max-height: 29.5rem;
}

.sensor-reading-col{
  max-height: inherit;
}

#root{
  flex-direction: column;
}
</style>