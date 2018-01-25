<template>
  <foreignObject
    v-show="selectedCattleInventory"
    class="fo" ref="tip" :height="$parent.bodyHeight" :width="tipWidth" y="0">
    <body xmlns="http://www.w3.org/1999/xhtml">
      <table class="fo-table">
        <thead>
          <tr>
            <th>
              <span class="selected-year">{{ selectedYear }}</span>
            </th>
            <th class="inventory">Inventory</th>
            <th class="loss">Loss</th>
            <th>% Loss</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th>Cattle</th>
            <td class="inventory">
              <template v-if="selectedCattleInventory">
                {{ $parent.yFormat(selectedCattleInventory.value) }}
              </template>
              <template v-else>
                &mdash;
              </template>
            </td>
            <td class="loss">
              <template v-if="selectedCattleLoss">
                {{ $parent.yFormat(selectedCattleLoss.value) }}
              </template>
              <template v-else>
                &mdash;
              </template>
            </td>
            <td>
              <template v-if="selectedCattleInventory && selectedCattleLoss">
                {{ percentFormat(selectedCattleLoss.value / selectedCattleInventory.value) }}
              </template>
              <template v-else>
                &mdash;
              </template>
            </td>
          </tr>
          <tr>
            <th>Calves</th>
            <td class="inventory">
              <template v-if="selectedCalfInventory">
                {{ $parent.yFormat(selectedCalfInventory.value) }}
              </template>
              <template v-else>
                &mdash;
              </template>
            </td>
            <td class="loss">
              <template v-if="selectedCalfLoss">
                {{ $parent.yFormat(selectedCalfLoss.value) }}
              </template>
              <template v-else>
                &mdash;
              </template>
            </td>
            <td>
              <template v-if="selectedCalfInventory && selectedCalfLoss">
                {{ percentFormat(selectedCalfLoss.value / selectedCalfInventory.value) }}
              </template>
              <template v-else>
                &mdash;
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </body>
  </foreignObject>
</template>

<script>
import * as d3 from 'd3'
export default {
  data () {
    return {
      tipWidth: 165,
      tipGap: 25,
      selectedCattleInventory: null,
      selectedCattleLoss: null,
      selectedCalfInventory: null,
      selectedCalfLoss: null,
      selectedYear: null
    }
  },
  mounted () {
    this.attach()
  },
  computed: {
    yearBisector () {
      return d3.bisector(d => {
        return d.timestamp
      }).left
    },
    percentFormat () {
      return d3.format('.1%')
    }
  },
  methods: {
    attach () {
      d3.select(this.$parent.$refs.mouse)
        .on('mousemove', () => {
          let m = d3.mouse(d3.event.currentTarget)
          let x = m[0] - this.$parent.margin.left
          let domainX = this.$parent.x.invert(x)
          let search = new Date(domainX.getFullYear(), 0, 1)
          let tipX = (x + this.tipWidth + this.tipGap > this.$parent.bodyWidth)
            ? (x - this.tipWidth - this.tipGap)
            : x + this.tipGap
          d3.select(this.$refs.tip)
            .attr('x', tipX)

          let cattleInventoryIndex = this.yearBisector(this.$parent.cattleInventoryData, search)
          this.selectedCattleInventory = cattleInventoryIndex
            ? this.$parent.cattleInventoryData[cattleInventoryIndex]
            : null
          if (this.selectedCattleInventory) {
            this.selectedYear = this.selectedCattleInventory.year
          }
          let cattleLossIndex = this.yearBisector(this.$parent.cattleLossData, search)
          this.selectedCattleLoss = cattleLossIndex
            ? this.$parent.cattleLossData[cattleLossIndex]
            : null
          let calfInventoryIndex = this.yearBisector(this.$parent.calfInventoryData, search)
          this.selectedCalfInventory = calfInventoryIndex
            ? this.$parent.calfInventoryData[calfInventoryIndex]
            : null
          let calfLossIndex = this.yearBisector(this.$parent.calfLossData, search)
          this.selectedCalfLoss = calfLossIndex
            ? this.$parent.calfLossData[calfLossIndex]
            : null
        })
        .on('mouseout', () => {
          this.selectedCattleInventory = null
        })
    }
  }
}
</script>

<style>
.fo {
  background: rgba(255, 255, 255, 0.75);
  border: 1px solid #ddd;
  border-bottom: none;
  border-top: none;
  font-size: 0.75em;
}
.fo-table td, .fo-table th {
  padding: 0.1em 0.25em;
  text-align: right;
}

.selected-year {
  border-radius: 0.25em;
  padding: 0 0.25em;
  background: rgba(0, 0, 0, 0.2);
}
.inventory {
  color: steelblue;
}
.loss {
  color: firebrick;
}
</style>
