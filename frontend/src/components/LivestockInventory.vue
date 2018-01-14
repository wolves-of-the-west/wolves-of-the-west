<template>
  <v-card flat>
    <v-card-text>
      <v-layout row wrap>
        <v-flex sm12 md4 lg6>
          <section class="graph-info">
            <h1 class="title">{{ title }}</h1>
            <h2 class="sub-title" v-if="loaded">
              {{ xFormat(xExtent[0]) }}
              &ndash;
              {{ xFormat(xExtent[1]) }}
              <span class="diff">
                ({{ xExtent[1].getFullYear() - xExtent[0].getFullYear() }} years)
              </span>
            </h2>
            <small class="source">
              <strong>Source:</strong> <a href="https://quickstats.nass.usda.gov" target="_blank">USDA National Agricultural Statistics Service</a>
            </small>
          </section>
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
                Show:
                <v-radio-group v-model="focus">
                  <v-radio label="National and State" value="all"/>
                  <v-radio label="State" value="state"/>
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
      <div class="loader" v-if="!loaded">
        <icon name="spinner" spin/> Loading&hellip;
      </div>
      <livestock-inventory-annotations
        v-if="loaded"
        :leftMargin="margin.left"
        :xDomain="xDomain"
        :width="width"
        :x="x"/>
      <svg :viewBox="viewBox">
        <g ref="xAxis"/>
        <g ref="yAxis"/>
        <clipPath id="bodyClipPath">
          <rect x="0" y="0" :width="bodyWidth" :height="bodyHeight"/>
        </clipPath>
        <rect
          :x="margin.left" :y="margin.top"
          ref="mouse" class="mouse"
          :width="bodyWidth" :height="bodyHeight"/>
        <text ref="nationalLabel"/>
        <text ref="stateLabel" v-show="focus == 'all'"/>
        <g ref="stateLabels" v-show="focus == 'state'"/>
        <g ref="body" clip-path="url(#bodyClipPath)">
          <g ref="stateLines"/>
          <path ref="nationalLine" class="inventory-line"/>
          <line ref="wolfReintroLine" class="wolf-line"/>
          <line ref="wolfSecondReintroLine" class="wolf-line"/>
          <line ref="wolfLastKilledInYellowstoneLine" class="wolf-line"/>
          <g ref="tips"/>
        </g>
      </svg>
    </v-card-text>
  </v-card>
</template>

<script>
import * as d3 from 'd3'
import axios from 'axios'
import * as numeral from 'numeral'
import { mapGetters } from 'vuex'
import { annotation, annotationCalloutCircle } from 'd3-svg-annotation'
import LivestockInventoryAnnotations from './LivestockInventoryAnnotations'
export default {
  props: ['title', 'type'],
  components: {
    LivestockInventoryAnnotations
  },
  data () {
    return {
      loaded: false,
      margin: {
        top: 5,
        right: 100,
        bottom: 20,
        left: 50
      },
      height: 125,
      width: 1200,
      stateLabelHeight: 14,
      focus: 'all'
    }
  },
  computed: {
    ...mapGetters([
      'earliestWolfReintroductionYear',
      'latestWolfReintroductionYear',
      'lastWolfKilledInYellowstone'
    ]),
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
    },
    allData () {
      return [].concat(this.national).concat(this.state)
    },
    stateColor () {
      return d3.scaleOrdinal(d3.schemeCategory10)
    },
    nationalData () {
      return this.national
    },
    bodyHeight () {
      return this.height - this.margin.top - this.margin.bottom
    },
    halfBodyHeight () {
      return this.bodyHeight * 0.5
    },
    bodyWidth () {
      return this.width - this.margin.left - this.margin.right
    },
    halfBodyWidth () {
      return this.bodyWidth * 0.5
    },
    bodyEl () {
      return d3.select(this.$refs.body)
    },
    nationalLineEl () {
      return d3.select(this.$refs.nationalLine)
    },
    lineFn () {
      return d3.line()
        .x(d => { return this.x(d.timestamp) })
        .y(d => { return this.yScale(d.value) })
        .curve(d3.curveMonotoneX)
    },
    x () {
      return d3.scaleTime()
        .domain(this.xExtent)
        .range([0, this.bodyWidth])
    },
    xExtent () {
      let extent = d3.extent(this.allData, d => { return d.timestamp })
      return [
        d3.timeYear.offset(extent[0], -1),
        d3.timeYear.offset(extent[1], 1)
      ]
    },
    xWolfExtent () {
      let xMax = this.xExtent[1]
      let xMin = this.earliestWolfReintroductionYear - (xMax - this.earliestWolfReintroductionYear)
      return [xMin, xMax]
    },
    xAxis () {
      return d3.axisBottom(this.x)
        .tickFormat(this.xFormat)
    },
    xAxisEl () {
      return d3.select(this.$refs.xAxis)
    },
    yLinear () {
      return d3.scaleLinear()
        .domain([0, this.yMax])
        .range([this.bodyHeight, 0])
        .nice()
    },
    yLog () {
      return d3.scaleLog()
        .domain([1, this.yMax])
        .range([this.bodyHeight, 0])
        .nice()
    },
    yScale () {
      return this.yIsLinear ? this.yLinear : this.yLog
    },
    yAxis () {
      return d3.axisLeft(this.yScale)
        .tickFormat(this.yFormat)
        .ticks(5)
    },
    yAxisEl () {
      return d3.select(this.$refs.yAxis)
    },
    yMin () {
      return this.yIsLinear ? 0 : 1
    },
    yMax () {
      switch (this.focus) {
        case 'state':
          return d3.max(this.state, d => { return d.value })
        case 'all':
          return d3.max(this.allData, d => { return d.value })
      }
    },
    viewBox () {
      return [0, 0, this.width, this.height].join(' ')
    },
    xFormat () {
      return d3.timeFormat('%Y')
    },
    stateData () {
      return this.state.map(d => {
        d.x = this.x(d.timestamp)
        return d
      })
    },
    nestedStateData () {
      return d3.nest()
        .key(d => { return d.state })
        .entries(this.stateData)
    },
    stateMean () {
      return d3.mean(this.stateData, d => { return d.value })
    },
    yIsLinear () {
      return this.usdaYScaleType === 'linear'
    },
    wolfReintroLine () {
      return d3.select(this.$refs.wolfReintroLine)
    },
    wolfSecondReintroLine () {
      return d3.select(this.$refs.wolfSecondReintroLine)
    },
    wolfLastKilledInYellowstoneLine () {
      return d3.select(this.$refs.wolfLastKilledInYellowstoneLine)
    },
    xDomain () {
      return this.usdaTimeWindow === 'all' ? this.xExtent : this.xWolfExtent
    },
    yearBisector () {
      return d3.bisector(d => {
        return d.timestamp
      }).right
    },
    fetchStateData () {
      return axios.get(`${API_URL}/${this.type.toLowerCase()}/inventory/state?state=All`) // eslint-disable-line no-undef
    },
    fetchNationalData () {
      return axios.get(`${API_URL}/${this.type.toLowerCase()}/inventory/national`) // eslint-disable-line no-undef
    }
  },
  methods: {
    yFormat (value) {
      return numeral(value).format('0.0a')
    },
    setup () {
      this.bodyEl.attr(
        'transform',
        `translate(${this.margin.left}, ${this.margin.top})`
      )
      this.yAxisEl.attr(
        'transform',
        `translate(${this.margin.left}, ${this.margin.top})`
      )
      this.xAxisEl.attr(
        'transform',
        `translate(${this.margin.left}, ${this.height - this.margin.bottom})`
      )
      d3.select(this.$refs.mouse)
        .on('mousemove', () => {
          let m = d3.mouse(d3.event.currentTarget)
          let x = m[0] - this.margin.left
          let domainX = this.x.invert(x)
          let search = new Date(domainX.getFullYear(), 0, 1)
          let index = this.yearBisector(this.nationalData, search)
          if (this.national[index]) {
            this.tip(this.national[index])
          }
        })
        .on('mouseout', () => {
          d3.select(this.$refs.tips).selectAll('g').remove()
        })

      this.graph()
    },
    graph () {
      this.x.domain(this.xDomain)

      let t = d3.transition().duration(1000)
      this.yAxisEl.transition(t).call(this.yAxis)
      this.xAxisEl.transition(t).call(this.xAxis)

      this.graphNational(t)
      this.graphState(t)
      this.graphWolfInfo(t)
    },
    graphWolfInfo (t) {
      this.wolfReintroLine
        .transition(t)
        .attr('x1', this.x(this.earliestWolfReintroductionYear))
        .attr('x2', this.x(this.earliestWolfReintroductionYear))
        .attr('y1', this.yScale(this.yMin))
        .attr('y2', 0)
      this.wolfSecondReintroLine
        .transition(t)
        .attr('x1', this.x(this.latestWolfReintroductionYear))
        .attr('x2', this.x(this.latestWolfReintroductionYear))
        .attr('y1', this.yScale(this.yMin))
        .attr('y2', 0)
      this.wolfLastKilledInYellowstoneLine
        .transition(t)
        .attr('x1', this.x(this.lastWolfKilledInYellowstone))
        .attr('x2', this.x(this.lastWolfKilledInYellowstone))
        .attr('y1', this.yScale(this.yMin))
        .attr('y2', 0)
    },
    graphState (t) {
      let stateLine = d3.select(this.$refs.stateLines)
        .selectAll('.inventory-line')
        .data(this.nestedStateData)

      stateLine.enter()
        .append('path')
        .attr('class', 'inventory-line')
        .merge(stateLine)
          .transition(t)
          .style('stroke', d => {
            return this.stateColor(d.key)
          })
          .attr('d', d => {
            return this.lineFn(d.values)
          })

      d3.select(this.$refs.stateLabel)
        .transition(t)
        .attr('text-anchor', 'start')
        .attr('x', this.bodyWidth + this.margin.left)
        .attr('y', this.yScale(this.stateMean) + 4)
        .text('Western States')

      this.graphStateLabels(t)
    },
    graphStateLabels (t) {
      let labels = this.nestedStateData.map(d => {
        return {
          state: d.key,
          fx: 0,
          targetY: d.values[d.values.length - 1].value
        }
      })
      let forceClamp = (min, max) => {
        let nodes
        const force = () => {
          nodes.forEach(n => {
            if (n.y > max) n.y = max
            if (n.y < min) n.y = min
          })
        }
        force.initialize = (_) => {
          nodes = _
        }
        return force
      }
      let force = d3.forceSimulation()
        .nodes(labels)
        .force('collide', d3.forceCollide(this.stateLabelHeight / 2))
        .force('y', d3.forceY(d => this.yScale(d.targetY)).strength(1))
        .force('clamp', forceClamp(this.margin.top + (this.stateLabelHeight * 0.5), this.bodyHeight))
        .stop()

      for (let i = 0; i < 300; i++) force.tick()

      let legend = d3.select(this.$refs.stateLabels)
        .attr('transform', `translate(${this.bodyWidth + this.margin.left}, 0)`)
      let legendItems = legend.selectAll('.legend-item').data(labels)
      legendItems.exit().remove()
      legendItems.transition(t).attr('y', d => d.y)
      legendItems.enter().append('text')
        .attr('class', 'legend-item')
        .attr('fill', d => this.stateColor(d.state))
        .attr('font-size', this.labelHeight)
        .attr('alignment-baseline', 'middle')
        .attr('x', 0)
        .attr('dx', '.5em')
        .attr('y', d => d.y)
        .text(d => d.state)
    },
    graphNational (t) {
      this.nationalLineEl
        .datum(this.nationalData)
        .transition(t)
        .attr('d', this.lineFn)
      d3.select(this.$refs.nationalLabel)
        .transition(t)
        .attr('text-anchor', 'start')
        .attr('x', this.bodyWidth + this.margin.left)
        .attr('y', this.yScale(this.national[this.national.length - 1].value) + 8)
        .text('National')
    },
    tip (d) {
      let annotationtip = annotation()
        .type(annotationCalloutCircle)
        .annotations([d].map(d => {
          return {
            data: d,
            dx: this.x(d.timestamp) > this.halfBodyWidth ? -10 : 10,
            dy: this.yScale(d.value) > this.halfBodyHeight ? -85 : 85,
            note: {
              title: d.year,
              label: this.yFormat(d.value)
            },
            subject: {
              radius: 5,
              radiusPadding: 0
            }
          }
        }))
        .accessors({
          x: d => this.x(d.timestamp),
          y: d => this.yScale(d.value)
        })
      d3.select(this.$refs.tips).call(annotationtip)
    },
    fetchData () {
      return axios.all([this.fetchNationalData, this.fetchStateData])
        .then(axios.spread((national, state) => {
          this.national = this.objectifyTimestamps(national.data)
          this.state = this.objectifyTimestamps(state.data.data)
          this.loaded = true
          this.setup()
        }))
    },
    objectifyTimestamps (arr) {
      return arr.map(d => {
        d.timestamp = new Date(d.timestamp)
        return d
      })
    }
  },
  watch: {
    focus () {
      this.graph()
    },
    usdaTimeWindow () {
      this.graph()
    },
    usdaYScaleType () {
      this.yAxis.scale(this.yScale)
      this.graph()
    },
    type: {
      immediate: true,
      handler: function () {
        this.fetchData()
      }
    }
  }
}
</script>

<style>
.inventory-line {
  stroke: steelblue;
  stroke-width: 1px;
  fill: none;
}
.wolf-line {
  stroke: slategray;
  stroke-width: 1px;
  stroke-dasharray: 4;
  pointer-events: none;
}
.graph {
  margin-top: -0.5em;
}
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
.mouse {
  fill: none;
  pointer-events: all;
}
.diff {
  opacity: 0.5;
}
.input-group__details {
  display: none;
}
.source {
  font-style: italic;
}
.loader {
  margin-top: 1em;
}
.graph-info {
  margin-bottom: 1em;
}

@media (max-width: 600px) {
  .actions .flex + .flex {
    margin-top: 1em;
  }
}
</style>
