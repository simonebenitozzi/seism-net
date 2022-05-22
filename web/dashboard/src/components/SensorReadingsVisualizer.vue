<template>
  <md-card>
    <LineChartGenerator
      :chartData="chartData"
      :width="chartWidth"
      :height="chartHeight"
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
        return [1, 2, 3, 4, 1, 2, 3, 4];
      },
    },
    labels: {
      type: Array,
      default: () => {
        ["1", "2", "3", "4", "1", "2", "3", "4"];
      },
    },
    datasetName:{
      type: String,
      default: "Readings"
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
            borderColor: "red",
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