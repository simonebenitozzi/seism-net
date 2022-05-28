<template>
  <md-table
    v-model="events"
    :md-sort.sync="currentSort"
    :md-sort-order.sync="currentSortOrder"
    class="table"
  >
    <md-table-row slot="md-table-row" slot-scope="{ item }">
      <md-table-cell md-label="Timestamp" md-sort-by="timestamp">{{
        item.timestamp
      }}</md-table-cell>
      <md-table-cell md-label="Frequency(Hz)" md-numeric>{{
        item.frequency
      }}</md-table-cell>
      <md-table-cell md-label="Magnitude" md-numeric md-sort-by="magnitude">{{
        item.magnitude
      }}</md-table-cell>
      <md-table-cell md-label="Mercalli scale" md-numeric md-sort-by="mercalli">{{
        item.mercalli
      }}</md-table-cell>
    </md-table-row>
  </md-table>
  
</template>

<script>
export default {
  name: "SeismicEventsVisualizer",
  props: {
    events: {
      type: Array,
      default: () => {
        return [
          {
            timestamp: new Date(Date.now()).toISOString(),
            frequency: 10,
            magnitude: 0.54,
            mercalli: 7,
          },
        ];
      },
    },
  },

  data: () => {
    return {
      currentSort: "timestamp",
      currentSortOrder: "desc",
    };
  },
};
</script>

<style scoped>
.table{
  height: 95%;
  max-height: 95%;
}
</style>