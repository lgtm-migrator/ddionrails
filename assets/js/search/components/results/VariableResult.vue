<template>
  <div class="card-body">
    <p class="card-title">
      <i class="fa fa-chart-bar"></i>
      <a :href="baseUrl + '/variable/' + item._id">
        [
        <span v-html="item.name"></span>]
        <span v-html="item.label"></span>
      </a>
    </p>
    <p class="card-text">
      Variable in study:
      <a
        :href="'/' + item.study.name"
        v-html="item.study.label">
      </a>
      |
      dataset:
      <a
        :href="'/' + item.study.name + '/data/' + item.dataset.name"
        :title="item.dataset.label"
        v-html="item.dataset.name">
      </a>
      |
      period:
      <span v-if="item.period">{{ item.period }}</span>
      <span v-else>None</span> |
      analysis unit:
      <span v-if="item.analysis_unit">{{ item.analysis_unit }}</span>
      <span v-else>None</span>
    </p>
  </div>
</template>

<script>
export default {
  name: "VariableResult",
  props: ["item"],
  data: function() {
    return {
      baseUrl: window.location.origin
    };
  }
};
</script>
