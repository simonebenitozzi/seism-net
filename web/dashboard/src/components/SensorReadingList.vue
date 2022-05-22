<template>
  <div class="md-layout">
    <div
      class="md-layout-item md-size-20 sensor-reading-container"
      v-for="sensor in sensors"
      :key="sensor.id"
    >
      <SensorReadingsVisualizer
        :datapoints="sensor.getData()"
        :displayLimit="10"
        :labels="
          sensor.getTimestamps().map((ts) => {
            return ts.toLocaleTimeString();
          })
        "
        :datasetName="sensor.id"
      />
    </div>
    <md-button class="md-primary" @click="addData">Primary</md-button>
  </div>
</template>

<script>
import SensorReadingsVisualizer from "./SensorReadingsVisualizer.vue";
import { Sensor } from "../model/Sensor";
import { SensorHandler } from "../model/SensorHandler";

export default {
  name: "SensorReadingList",

  components: {
    SensorReadingsVisualizer,
  },

  data() {
    return {
      sensors: [
        new Sensor("1"),
        new Sensor("2"),
        new Sensor("3"),
        new Sensor("4"),
        new Sensor("5"),
      ],

      sensorHandler: new SensorHandler(),
    };
  },

  methods: {
    addData() {
      this.sensors[0].appendData(6, new Date(Date.now()));
    },
  },
};
</script>

<style scoped>
.sensor-reading-container {
  margin-bottom: 2rem;
}
</style>