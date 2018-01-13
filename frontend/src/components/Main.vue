<template>
  <div>
    <intro/>
    <livestock-inventory type="Cattle" title="Yearly Cattle Inventory"/>
  </div>
</template>

<script>
import Intro from '@/components/Intro'
import LivestockInventory from '@/components/LivestockInventory'
export default {
  components: {
    Intro,
    LivestockInventory
  }
}
</script>
