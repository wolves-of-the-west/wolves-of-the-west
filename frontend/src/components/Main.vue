<template>
  <div>
    <intro/>
    <livestock-inventory type="Cattle" title="Yearly Cattle Inventory"/>
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
  </div>
</template>

<script>
import Intro from '@/components/Intro'
import LivestockInventory from '@/components/LivestockInventory'
import StateLivestockInventory from '@/components/StateLivestockInventory'
export default {
  components: {
    Intro,
    LivestockInventory,
    StateLivestockInventory
  }
}
</script>
