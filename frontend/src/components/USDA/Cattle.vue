<template>
  <v-card raised>
    <v-card-text>
      <v-layout row wrap>
        <v-flex sm12 md4 lg6>
          <h1 class="display-1">Cattle and Calves</h1>
          <h2 class="subheading">Inventory, Crop, and Loss by Year</h2>
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
                <svg class="legend-line">
                  <line x1="0" x2="10" y1="10" y2="0" class="adult-inventory-line"/>
                </svg>
                Cattle Inventory
                <br>
                <svg class="legend-line">
                  <line x1="0" x2="10" y1="10" y2="0" class="adult-loss-line"/>
                </svg>
                Cattle Loss
                <br>
                <svg class="legend-line">
                  <line x1="0" x2="10" y1="10" y2="0" class="youth-inventory-line"/>
                </svg>
                Calf Crop
                <br>
                <svg class="legend-line">
                  <line x1="0" x2="10" y1="10" y2="0" class="youth-loss-line"/>
                </svg>
                Calf Loss
              </v-flex>
              <v-flex xs12 sm4>
                Zoom to:
                <v-radio-group v-model="usdaTimeWindow">
                  <v-radio label="All data" value="all"/>
                  <v-radio label="Wolf reintroductions" value="wolf"/>
                </v-radio-group>
              </v-flex>
              <v-flex xs12 sm4>
                Scale as:
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
      <hr/>
      <v-layout row wrap>
        <v-flex xs12>
          <p>
            This data is sourced from
            <a href="https://quickstats.nass.usda.gov" target="_blank">Quick Stats</a> &mdash;
            a database provided by the USDA's National Agricultural Statistics Service.
          </p>
          <div class="legend-row">
            <svg class="legend-line">
              <line x1="0" x2="10" y1="10" y2="0" class="adult-inventory-line"/>
            </svg>
            <p class="legend-info">
              <strong>Cattle Inventory</strong> is not provided as a data point.
              It must be derived by subtracting <span class="data-item">CATTLE, CALVES - INVENTORY</span> from <span class="data-item">CATTLE, INCL CALVES - INVENTORY</span>.
            </p>
          </div>
          <div class="legend-row">
            <svg class="legend-line">
              <line x1="0" x2="10" y1="10" y2="0" class="adult-loss-line"/>
            </svg>
            <p class="legend-info">
              <strong>Cattle Loss</strong> is <span class="data-item">CATTLE, (EXCL CALVES) - LOSS, DEATH, MEASURED IN HEAD</span>.
            </p>
          </div>
          <div class="legend-row">
            <svg class="legend-line">
              <line x1="0" x2="10" y1="10" y2="0" class="youth-inventory-line"/>
            </svg>
            <p class="legend-info">
              <strong>Calf Crop</strong> is <span class="data-item">CATTLE - CALF CROP, MEASURED IN HEAD</span>. Note that <a href="https://quickstats.nass.usda.gov" target="_blank">Quick Stats</a> provides a calf inventory and a calf crop. The crop is how many calves were born, whereas inventory is the number of calves. This is an important distinction because once calves exceed 499 pounds they are considered cattle.
            </p>
          </div>
          <div class="legend-row">
            <svg class="legend-line">
              <line x1="0" x2="10" y1="10" y2="0" class="youth-loss-line"/>
            </svg>
            <p class="legend-info">
              <strong>Calf Loss</strong> is <span class="data-item">CATTLE, CALVES - LOSS, DEATH, MEASURED IN HEAD</span>.
            </p>
          </div>
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
.legend-row {
  display: flex;
}
.legend-line {
  margin-top: 0.5em;
  flex: 0 0 1em;
  width: 10px;
  height: 10px;
  margin-right: 0.5em;
}
.legend-line line {
  stroke-width: 2px;
}
hr {
  margin: 1.5em 0;
  opacity: 0.5;
}
.data-item {
  color: slategray;
}
</style>