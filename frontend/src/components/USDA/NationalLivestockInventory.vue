<template>
  <div>
    <h1 class="title">National</h1>
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
      <g ref="body" clip-path="url(#bodyClipPath)">
        <path ref="cattleInventoryLine" class="adult-inventory-line"/>
        <path ref="calfInventoryLine" class="youth-inventory-line"/>
        <path ref="cattleLossLine" class="adult-loss-line"/>
        <path ref="calfLossLine" class="youth-loss-line"/>
        <line ref="wolfReintroLine" class="wolf-line"/>
        <line ref="wolfSecondReintroLine" class="wolf-line"/>
        <line ref="wolfLastKilledInYellowstoneLine" class="wolf-line"/>
        <hoverable-data/>
      </g>
    </svg>
  </div>
</template>

<script>
import * as d3 from 'd3'
import axios from 'axios'
import * as numeral from 'numeral'
import { mapGetters } from 'vuex'
import LivestockInventoryAnnotations from './LivestockInventoryAnnotations'
import HoverableData from '@/components/HoverableData'
export default {
  props: ['type'],
  components: {
    HoverableData,
    LivestockInventoryAnnotations
  },
  data () {
    return {
      cattleInventoryData: [],
      calfInventoryData: [],
      cattleLossData: [],
      calfLossData: [],
      loaded: false,
      margin: {
        top: 5,
        right: 20,
        bottom: 20,
        left: 50
      },
      height: 100,
      width: 1200
    }
  },
  computed: {
    ...mapGetters([
      'earliestWolfReintroductionYear',
      'latestWolfReintroductionYear',
      'lastWolfKilledInYellowstone',
      'usdaTimeWindow',
      'usdaYScaleType'
    ]),
    allData () {
      return this.cattleInventoryData.concat(
        this.calfInventoryData.concat(
          this.cattleLossData.concat(
            this.calfLossData
          )
        )
      )
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
      return d3.extent(this.allData, d => { return d.timestamp })
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
        .ticks(4)
    },
    yAxisEl () {
      return d3.select(this.$refs.yAxis)
    },
    yMin () {
      return this.yIsLinear ? 0 : 1
    },
    yMax () {
      return d3.max(this.allData, d => { return d.value })
    },
    viewBox () {
      return [0, 0, this.width, this.height].join(' ')
    },
    xFormat () {
      return d3.timeFormat('%Y')
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
    fetchNationalData () {
      return axios.get(`${API_URL}/usda/${this.type.toLowerCase()}/national`) // eslint-disable-line no-undef
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
      this.graph()
    },
    graph () {
      this.x.domain(this.xDomain)

      let t = d3.transition().duration(1000)
      this.yAxisEl.transition(t).call(this.yAxis)
      this.xAxisEl.transition(t).call(this.xAxis)

      this.graphNational(t)
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
    graphNational (t) {
      d3.select(this.$refs.cattleInventoryLine)
        .datum(this.cattleInventoryData)
        .transition(t)
        .attr('d', this.lineFn)
      d3.select(this.$refs.calfInventoryLine)
        .datum(this.calfInventoryData)
        .transition(t)
        .attr('d', this.lineFn)
      d3.select(this.$refs.cattleLossLine)
        .datum(this.cattleLossData)
        .transition(t)
        .attr('d', this.lineFn)
      d3.select(this.$refs.calfLossLine)
        .datum(this.calfLossData)
        .transition(t)
        .attr('d', this.lineFn)
    },
    fetchData () {
      return this.fetchNationalData.then(response => {
        this.cattleInventoryData = this.objectifyTimestamps(response.data.cattleInventoryData)
        this.calfInventoryData = this.objectifyTimestamps(response.data.calfInventoryData)
        this.cattleLossData = this.objectifyTimestamps(response.data.cattleLossData)
        this.calfLossData = this.objectifyTimestamps(response.data.calfLossData)
        this.loaded = true
        this.setup()
      })
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
.wolf-line {
  stroke: slategray;
  stroke-width: 1px;
  stroke-dasharray: 4;
  pointer-events: none;
}
.graph {
  margin-top: -0.5em;
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
.loader {
  margin-top: 1em;
}

@media (max-width: 600px) {
  .actions .flex + .flex {
    margin-top: 1em;
  }
}
</style>
