<template>
  <md-card>
    <LineChartGenerator
      class="chart"
      :chartData="chartData"
      :width="chartWidth"
      :height="chartHeight"
      :chartOptions="{
        spanGaps: true,
        animation: false,
        plugins: {
          tooltip: { enabled: false },
          title:{
            display: !sensorOnline,
            text: 'Offline',
            fullSize: true,
            color: 'red'
          }
        },
        responsive: true,
        scales: {
          y: {
            min: -.5,
            max: .5,
            beginAtZero: true,
          },
        },
      }"
    />
  </md-card>
</template>

<script>
import { Line as LineChartGenerator } from "vue-chartjs/legacy";
// eslint-disable-next-line no-unused-vars
import Chart from "chart.js/auto";

export default {
  components: { LineChartGenerator },
  props: {
    datapoints: {
      type: Array,
      default: () => {
        return [0.3, 0.4, 0.5, -0.6, -1.4, -0.5, -0.2, 0];
      },
    },
    labels: {
      type: Array,
      default: () => {
        ["1", "2", "3", "4", "1", "2", "3", "4"];
      },
    },
    datasetName: {
      type: String,
      default: "Readings",
    },
    chartHeight: {
      type: Number,
      default: 200,
    },
    chartWidth: {
      type: Number,
      default: 400,
    },
    displayLimit: {
      type: Number,
      default: null,
    },
    sensorOnline:{
      type: Boolean,
      default : true
    }
  },
  data() {
    return {
      chart: null,
    };
  },

  computed: {
    chartData() {
      return {
        labels: this.filteredLabels,
        datasets: [
          {
            label: this.datasetName,
            data: this.filteredData,
            borderColor: "blue",
            fill: false,
            pointRadius: 0,
          },
        ],
      };
    },

    filteredData() {
      let result = this.datapoints;
      if (this.displayLimit != null) {
        let lowerInclusiveIndex = result.length - this.displayLimit;
        lowerInclusiveIndex = Math.max(lowerInclusiveIndex, 0);
        result = result.slice(lowerInclusiveIndex, result.length - 1);
      }
      return result;
    },

    filteredLabels() {
      let result = this.labels;
      if (this.displayLimit != null) {
        let lowerInclusiveIndex = result.length - this.displayLimit;
        lowerInclusiveIndex = Math.max(lowerInclusiveIndex, 0);
        result = result.slice(lowerInclusiveIndex, result.length - 1);
      }
      return result;
    },
  },
};
</script>

<style scoped>
.chart{
  max-height: inherit;
}
</style>