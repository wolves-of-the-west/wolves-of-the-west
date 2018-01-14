import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export const store = new Vuex.Store({
  state: {
    earliestWolfReintroductionYear: new Date(1995, 0, 1),
    latestWolfReintroductionYear: new Date(1996, 0, 1),
    lastWolfKilledInYellowstone: new Date(1926, 0, 1),
    usdaTimeWindow: 'all',
    usdaYScaleType: 'linear'
  },
  getters: {
    earliestWolfReintroductionYear: state => {
      return state.earliestWolfReintroductionYear
    },
    latestWolfReintroductionYear: state => {
      return state.latestWolfReintroductionYear
    },
    lastWolfKilledInYellowstone: state => {
      return state.lastWolfKilledInYellowstone
    },
    usdaTimeWindow: state => {
      return state.usdaTimeWindow
    },
    usdaYScaleType: state => {
      return state.usdaYScaleType
    }
  },
  mutations: {
    setUsdaTimeWindow: (state, payload) => {
      state.usdaTimeWindow = payload
    },
    setUsdaYScaleType: (state, payload) => {
      state.usdaYScaleType = payload
    }
  }
})
