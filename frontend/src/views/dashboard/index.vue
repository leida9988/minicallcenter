<template>
  <div class="dashboard-container">
    <!-- 数据卡片 -->
    <el-row :gutter="20">
      <el-col :xs="12" :sm="6" :lg="3" v-for="(item, index) in statsCard" :key="index">
        <div class="stats-card" :class="item.class">
          <div class="stats-info">
            <p class="stats-title">{{ item.title }}</p>
            <h3 class="stats-value">{{ item.value }}</h3>
            <p class="stats-desc">
              <span :class="item.trend === 'up' ? 'text-success' : 'text-danger'">
                <el-icon v-if="item.trend === 'up'"><CaretTop /></el-icon>
                <el-icon v-else><CaretBottom /></el-icon>
                {{ item.percent }}%
              </span>
              {{ item.desc }}
            </p>
          </div>
          <div class="stats-icon">
            <el-icon :size="40"><component :is="item.icon" /></el-icon>
          </div>
        </div>
      </el-col>
    </el-row>
    <!-- 图表区域 -->
    <el-row :gutter="20" class="mt-20">
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="card-header">
            <h3>今日通话趋势</h3>
          </div>
          <div class="chart-content" ref="callChartRef" style="height: 350px;"></div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="card-header">
            <h3>客户状态分布</h3>
          </div>
          <div class="chart-content" ref="customerChartRef" style="height: 350px;"></div>
        </div>
      </el-col>
    </el-row>
    <el-row :gutter="20" class="mt-20">
      <el-col :xs="24" :lg="8">
        <div class="chart-card">
          <div class="card-header">
            <h3>坐席通话排行</h3>
          </div>
          <div class="chart-content" ref="agentChartRef" style="height: 350px;"></div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="16">
        <div class="chart-card">
          <div class="card-header">
            <h3>最近通话记录</h3>
            <el-button type="primary" text @click="$router.push('/call/record')">查看全部</el-button>
          </div>
          <el-table :data="recentCallRecords" stripe style="width: 100%">
            <el-table-column prop="caller" label="主叫号码" />
            <el-table-column prop="called" label="被叫号码" />
            <el-table-column prop="duration" label="通话时长" formatter="formatDuration" />
            <el-table-column prop="status" label="通话状态">
              <template #default="scope">
                <el-tag :type="getStatusTagType(scope.row.status)">
                  {{ getStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="通话时间" width="180" />
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import { formatDuration } from '@/utils/datetime'
// 统计卡片数据
const statsCard = ref([
  {
    title: '今日通话数',
    value: 128,
    percent: 12.5,
    trend: 'up',
    desc: '较昨日',
    icon: 'Phone',
    class: 'card-blue'
  },
  {
    title: '接通率',
    value: '85.6%',
    percent: 3.2,
    trend: 'up',
    desc: '较昨日',
    icon: 'Check',
    class: 'card-green'
  },
  {
    title: '跟进客户数',
    value: 46,
    percent: 2.8,
    trend: 'down',
    desc: '较昨日',
    icon: 'User',
    class: 'card-orange'
  },
  {
    title: '意向客户',
    value: 12,
    percent: 5.3,
    trend: 'up',
    desc: '较昨日',
    icon: 'Star',
    class: 'card-purple'
  }
])
// 最近通话记录
const recentCallRecords = ref([
  {
    caller: '13800138000',
    called: '13900139000',
    duration: 185,
    status: 2,
    created_at: '2024-05-13 14:30:25'
  },
  {
    caller: '13800138000',
    called: '13700137000',
    duration: 246,
    status: 2,
    created_at: '2024-05-13 14:25:12'
  },
  {
    caller: '13800138000',
    called: '13600136000',
    duration: 0,
    status: 4,
    created_at: '2024-05-13 14:20:05'
  },
  {
    caller: '13800138000',
    called: '13500135000',
    duration: 128,
    status: 2,
    created_at: '2024-05-13 14:15:42'
  },
  {
    caller: '13800138000',
    called: '13400134000',
    duration: 0,
    status: 5,
    created_at: '2024-05-13 14:10:36'
  }
])
const callChartRef = ref(null)
const customerChartRef = ref(null)
const agentChartRef = ref(null)
// 初始化通话趋势图
const initCallChart = () => {
  if (!callChartRef.value) return
  const chart = echarts.init(callChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['通话数', '接通数']
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '23:59']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '通话数',
        type: 'line',
        data: [12, 8, 24, 45, 32, 28, 15],
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.5)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
          ])
        }
      },
      {
        name: '接通数',
        type: 'line',
        data: [8, 5, 18, 38, 27, 22, 10],
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103, 194, 58, 0.5)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.1)' }
          ])
        }
      }
    ]
  }
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}
// 初始化客户状态分布图
const initCustomerChart = () => {
  if (!customerChartRef.value) return
  const chart = echarts.init(customerChartRef.value)
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '客户状态',
        type: 'pie',
        radius: '50%',
        data: [
          { value: 1048, name: '待联系' },
          { value: 735, name: '联系中' },
          { value: 580, name: '有意向' },
          { value: 340, name: '已成交' },
          { value: 280, name: '已拒绝' },
          { value: 120, name: '无效客户' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}
// 初始化坐席通话排行图
const initAgentChart = () => {
  if (!agentChartRef.value) return
  const chart = echarts.init(agentChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      boundaryGap: [0, 0.01]
    },
    yAxis: {
      type: 'category',
      data: ['张三', '李四', '王五', '赵六', '钱七']
    },
    series: [
      {
        name: '通话时长(分钟)',
        type: 'bar',
        data: [240, 210, 185, 160, 140],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#409eff' },
            { offset: 1, color: '#67c23a' }
          ])
        }
      }
    ]
  }
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}
// 获取状态标签类型
const getStatusTagType = (status) => {
  const typeMap = {
    1: 'info',
    2: 'success',
    3: 'default',
    4: 'danger',
    5: 'warning',
    6: 'info'
  }
  return typeMap[status] || 'info'
}
// 获取状态文本
const getStatusText = (status) => {
  const textMap = {
    1: '呼叫中',
    2: '已接通',
    3: '已挂断',
    4: '未接通',
    5: '占线',
    6: '无人接听',
    7: '号码错误'
  }
  return textMap[status] || '未知'
}
onMounted(() => {
  initCallChart()
  initCustomerChart()
  initAgentChart()
})
</script>
<style lang="scss" scoped>
.dashboard-container {
  .stats-card {
    padding: 24px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    &:hover {
      transform: translateY(-3px);
      box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.15);
    }
    .stats-info {
      .stats-title {
        color: #666;
        font-size: 14px;
        margin-bottom: 8px;
      }
      .stats-value {
        color: #303133;
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 8px;
      }
      .stats-desc {
        color: #909399;
        font-size: 12px;
        .text-success {
          color: #67c23a;
        }
        .text-danger {
          color: #f56c6c;
        }
      }
    }
    .stats-icon {
      opacity: 0.8;
    }
    &.card-blue {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #fff;
      .stats-title,
      .stats-value,
      .stats-desc {
        color: #fff;
      }
    }
    &.card-green {
      background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      color: #fff;
      .stats-title,
      .stats-value,
      .stats-desc {
        color: #fff;
      }
    }
    &.card-orange {
      background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
      color: #fff;
      .stats-title,
      .stats-value,
      .stats-desc {
        color: #fff;
      }
    }
    &.card-purple {
      background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
      color: #fff;
      .stats-title,
      .stats-value,
      .stats-desc {
        color: #fff;
      }
    }
  }
  .chart-card {
    background: #fff;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;
      h3 {
        font-size: 16px;
        font-weight: bold;
        color: #303133;
      }
    }
    .chart-content {
      width: 100%;
    }
  }
}
</style>
