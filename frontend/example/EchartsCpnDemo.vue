<script setup lang="ts">
import { ref, onMounted } from "vue";

import * as echarts from "echarts";

onMounted(() => {
  renderChart(); // 生命周期挂载函数渲染图表
});
const renderChart = () => {
  const myRef = document.getElementById("canvars");
  const myChart = echarts.init(myRef!);
  myChart.setOption({
    title: {
      text: "ECharts 入门示例",
    },
    tooltip: {},
    xAxis: {
      data: ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"],
    },
    yAxis: {},
    series: [
      {
        name: "销量",
        type: "bar",
        data: [5, 20, 36, 10, 10, 20],
      },
    ],
  });
};
</script>

<template>
  <div class="canvars" id="canvars"></div>
</template>

<style lang="less" scoped>
.canvars {
  width: 200px;
  height: 200px;
}
</style>
