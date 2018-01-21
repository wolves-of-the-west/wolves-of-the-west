<template>
  <v-card flat>
    <v-card-text>
      <v-layout row wrap>
        <v-flex sm12 md4 lg6>
          <h1 class="display-1">Cattle</h1>
          <h2 class="subheading">Inventory and Loss by Year</h2>
          <h3 class="body-2" v-if="loaded">
            {{ xFormat(minYear) }}
            &ndash;
            {{ xFormat(maxYear) }}
            <span class="diff">
              ({{ numYears }} years)
            </span>
          </h3>
          <br>
        </v-flex>
        <v-flex sm12 md8 lg6 class="actions" v-if="loaded">
          <template v-if="loaded">
            <v-layout row wrap>
              <v-flex xs12 sm4>
                Zoom to:
                <v-radio-group v-model="usdaTimeWindow">
                  <v-radio label="All data" value="all"/>
                  <v-radio label="Wolf reintroductions" value="wolf"/>
                </v-radio-group>
              </v-flex>
              <v-flex xs12 sm4>
                Scale inventory as:
                <v-radio-group v-model="usdaYScaleType">
                  <v-radio label="Linear" value="linear"/>
                  <v-radio label="Logarithmic" value="log"/>
                </v-radio-group>
              </v-flex>
            </v-layout>
          </template>
        </v-flex>
      </v-layout>
      <v-layout row wrap>
        <v-flex xs12>
          <national-livestock-inventory type="Cattle"/>
        </v-flex>
      </v-layout>
      <v-layout row wrap>
        <v-flex xs12 sm6 md4>
          <state-livestock-inventory type="Cattle" state="Colorado"/>
        </v-flex>
        <v-flex xs12 sm6 md4>
          <state-livestock-inventory type="Cattle" state="Idaho"/>
        </v-flex>
        <v-flex xs12 sm6 md4>
          <state-livestock-inventory type="Cattle" state="Montana"/>
        </v-flex>
        <v-flex xs12 sm6 md4>
          <state-livestock-inventory type="Cattle" state="Oregon"/>
        </v-flex>
        <v-flex xs12 sm6 md4>
          <state-livestock-inventory type="Cattle" state="Washington"/>
        </v-flex>
        <v-flex xs12 sm6 md4>
          <state-livestock-inventory type="Cattle" state="Wyoming"/>
        </v-flex>
      </v-layout>
      <v-layout row wrap>
        <v-flex xs12>
          <p class="source">
            <strong>Source:</strong>&ensp;<a href="https://quickstats.nass.usda.gov" target="_blank">USDA National Agricultural Statistics Service</a>
          </p>
        </v-flex>
      </v-layout>
    </v-card-text>
  </v-card>
</template>

<script>
import * as d3 from 'd3'
import axios from 'axios'
import NationalLivestockInventory from '@/components/USDA/NationalLivestockInventory'
import StateLivestockInventory from '@/components/USDA/StateLivestockInventory'
export default {
  components: {
    StateLivestockInventory,
    NationalLivestockInventory
  },
  created () {
    this.fetchData()
  },
  data () {
    return {
      loaded: false,
      data: null
    }
  },
  computed: {
    xFormat () {
      return d3.timeFormat('%Y')
    },
    minYear () {
      return new Date(this.data.minYear, 1, 1)
    },
    maxYear () {
      return new Date(this.data.maxYear, 1, 1)
    },
    numYears () {
      return this.data.maxYear - this.data.minYear
    },
    usdaTimeWindow: {
      get () {
        return this.$store.getters.usdaTimeWindow
      },
      set (value) {
        this.$store.commit('setUsdaTimeWindow', value)
      }
    },
    usdaYScaleType: {
      get () {
        return this.$store.getters.usdaYScaleType
      },
      set (value) {
        this.$store.commit('setUsdaYScaleType', value)
      }
    }
  },
  methods: {
    fetchData () {
      axios.get(`${API_URL}/usda/cattle/stats`) // eslint-disable-line no-undef
        .then(response => {
          this.data = response.data
          this.loaded = true
        })
    }
  }
}
</script>

<style scoped>
.actions {
  background: #eee;
  border-radius: 0.3em;
  padding: 0.5em 1em;
}
.actions .radio-group {
  padding: 0;
}
.actions label {
  font-size: 1em;
}
.actions p {
  margin: 0;
}
.source {
  opacity: 0.75;
  margin-top: 1em;
  font-size: 0.75em;
}
</style>