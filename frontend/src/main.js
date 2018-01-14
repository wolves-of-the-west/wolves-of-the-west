// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import Vuetify from 'vuetify'
import App from './App'
import router from './router'

import 'vue-awesome/icons/spinner'
import Icon from 'vue-awesome/components/Icon'

import { store } from '@/store/store'

import './assets/index.css'

Vue.config.productionTip = false

Vue.use(Vuetify)
Vue.component('icon', Icon)

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  template: '<App/>',
  components: {
    App,
    Icon
  }
})
