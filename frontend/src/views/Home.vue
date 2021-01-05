
<template>

  <img alt="Vue logo" src="../assets/logo.png">

  <theheader></theheader>

  <div id="nav">
    <router-link to="/">Home</router-link> |
    <router-link to="/all">All</router-link> |
    <router-link to="/main/nvidia/3060">3060</router-link>
  </div>

  <div style="background: #42b983; margin: 0 auto; width: 500px">
    {{ thestring }}
  </div>


</template>
<script>


import axios from 'axios';
import theheader from "@/components/header";


export default {
  name: 'home',
  components: {theheader},
  data() {
    return {
    thestring: '',

    };
  },
  methods: {
    getMessage() {
      const path = 'http://localhost:5000/';
      axios.get(path)
          .then((res) => {

            this.thestring = res.data.thestring
          })
          .catch((error) => {
            // eslint-disable-next-line
            console.error(error);
          });


    },
  },
  created() {
    this.getMessage();
  },
};
</script>