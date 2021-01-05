<template>
    <div class="container">
      <div class="row">
        <div class="col-12 text-center">
        <div id="nav " class="">
          <router-link to="/">Home</router-link> |
          <router-link to="/all">All</router-link> |
          <router-link to="/main/nvidia/3060">3060</router-link>
        </div>
        </div>
      </div>
    </div>
</template>



<script>
import axios from 'axios';

export default {
  name: 'All',
  data() {
    return {

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
          })
    },
  },
  created() {
    this.getMessage();
  },
};
</script>