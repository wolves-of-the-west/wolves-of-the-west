<template>
  <svg :viewBox="viewBox">
    <g ref="annotations" class="annotation-group"/>
  </svg>
</template>

<script>
import * as d3 from 'd3'
import { annotation, annotationCallout } from 'd3-svg-annotation'
export default {
  props: ['width', 'x', 'leftMargin', 'xDomain'],
  data () {
    return {
      height: 100,
      earliestWolfReintroductionYear: new Date(1995, 1, 1),
      latestWolfReintroductionYear: new Date(1996, 1, 1),
      lastWolfKilledInYellowstone: new Date(1926, 1, 1)
    }
  },
  mounted () {
    this.graph()
  },
  computed: {
    yValue () {
      return this.height - 1
    },
    annotations () {
      return [
        {
          note: {
            label: 'Last wolf killed in Yellowstone',
            title: '1926',
            wrap: 500
          },
          data: {
            year: this.lastWolfKilledInYellowstone,
            value: this.yValue
          },
          dx: -25,
          dy: -25,
          connector: { end: 'arrow' }
        },
        {
          note: {
            label: 'Wolf reintroduction: 14 in Yellowstone; 15 in Idaho',
            title: this.xFormat(this.earliestWolfReintroductionYear),
            wrap: 125
          },
          data: {
            year: this.earliestWolfReintroductionYear,
            value: this.yValue
          },
          dx: -25,
          dy: -25,
          connector: { end: 'arrow' }
        },
        {
          note: {
            label: 'Wolf reintroduction: 17 in Yellowstone; 20 in Idaho',
            title: this.xFormat(this.latestWolfReintroductionYear),
            wrap: 125
          },
          data: {
            year: this.latestWolfReintroductionYear,
            value: this.yValue
          },
          dx: 25,
          dy: -25,
          connector: { end: 'arrow' }
        }
      ]
    },
    y () {
      return d3.scaleIdentity()
    },
    viewBox () {
      return [0, 0, this.width, this.height].join(' ')
    },
    xFormat () {
      return d3.timeFormat('%Y')
    },
    wolfAnnotations () {
      return annotation()
        .type(annotationCallout)
        .accessors({
          x: d => this.x(d.year),
          y: d => this.y(d.value)
        })
        .annotations(this.annotations)
    }
  },
  methods: {
    graph () {
      d3.select(this.$refs.annotations)
        .attr('transform', `translate(${this.leftMargin}, 0)`)
        .call(this.wolfAnnotations)
      d3.select(this.$refs.annotations).selectAll('.annotation')
        .transition()
        .duration(1000)
        .attrTween('transform', this.transformTween)
        .on('end', () => {
          this.wolfAnnotations.updatedAccessors()
        })
    },
    transformTween (d) {
      return d3.interpolateString(
        `translate(${d._x}, ${d._y})`,
        `translate(${this.x(d.data.year)}, ${d._y})`
      )
    }
  },
  watch: {
    x () {
      this.graph()
    },
    xDomain (x) {
      this.x.domain(this.xDomain)
      this.graph()
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
}
</style>
