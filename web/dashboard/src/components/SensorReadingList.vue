<template>
  <div class="md-layout">
    <div
      class="md-layout-item md-size-33 sensor-reading-container"
      v-for="sensor in sensors"
      :key="sensor.id"
    >
      <SensorReadingsVisualizer
        :datapoints="sensor.getData()"
        :displayLimit="50"
        :labels="
          sensor.getTimestamps().map((ts) => {
            return ts.toLocaleTimeString();
          })
        "
        :datasetName="sensor.id"
        :chartHeight="300"
        :sensorOnline="sensor.online"
      />
    </div>
  </div>
</template>

<script>
import SensorReadingsVisualizer from "./SensorReadingsVisualizer.vue";
import { SensorHandler } from "../model/SensorHandler";

export default {
  name: "SensorReadingList",

  components: {
    SensorReadingsVisualizer,
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

  computed:{
    sensors(){
      return this.sensorHandler.sensors;
    }
  }
};
</script>

<style scoped>
.sensor-reading-container {
  margin-bottom: 2rem;
}
</style>