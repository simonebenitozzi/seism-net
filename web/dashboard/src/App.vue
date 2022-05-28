<template>
  <md-app id="app">
    <md-app-toolbar class="md-primary">
      <span class="md-title">Seismograph net</span>
    </md-app-toolbar>
    <md-app-content>
      <Dashboard />
    </md-app-content>
  </md-app>
</template>

<script>
import Dashboard from "./components/Dashboard.vue";

export default {
  name: "App",
  components: {
    Dashboard,
  },
};
</script>

<style>
#app {
  height: 100vh;
  width: 100vw;
}
</style>
