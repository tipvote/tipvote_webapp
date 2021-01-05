import { createRouter,createWebHistory  } from 'vue-router'
import Home from '../views/Home.vue'
import All from "@/views/All";
import Nvidia3060 from "@/views/nvidia/Nvidia3060";


const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },

  {
    path: '/all',
    name: 'All',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: All
  },
  {
    path: '/main/nvidia/3060',
    name: 'Nvidia3060',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: Nvidia3060
  },
  // Always leave this as last one,
  // but you can also remove it

]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
