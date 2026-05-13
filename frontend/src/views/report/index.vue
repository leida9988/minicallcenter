<template>
  <div class="report-container">
    <div class="common-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-card total-calls">
            <div class="stat-icon">
              <el-icon size="32"><Phone /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ totalCalls }}</div>
              <div class="stat-label">总通话次数</div>
              <div class="stat-trend" :class="callTrend >= 0 ? 'up' : 'down'">
                <el-icon>{{ callTrend >= 0 ? 'CaretTop' : 'CaretBottom' }}</el-icon>
                <span>{{ Math.abs(callTrend) }}%</span>
              </div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card answer-rate">
            <div class="stat-icon">
              <el-icon size="32"><Check /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ answerRate }}%</div>
              <div class="stat-label">接通率</div>
              <div class="stat-trend" :class="answerRateTrend >= 0 ? 'up' : 'down'">
                <el-icon>{{ answerRateTrend >= 0 ? 'CaretTop' : 'CaretBottom' }}</el-icon>
                <span>{{ Math.abs(answerRateTrend) }}%</span>
              </div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card avg-duration">
            <div class="stat-icon">
              <el-icon size="32"><Timer /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ avgDuration }}</div>
              <div class="stat-label">平均通话时长</div>
              <div class="stat-trend" :class="durationTrend >= 0 ? 'up' : 'down'">
                <el-icon>{{ durationTrend >= 0 ? 'CaretTop' : 'CaretBottom' }}</el-icon>
                <span>{{ Math.abs(durationTrend) }}%</span>
              </div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card conversion-rate">
            <div class="stat-icon">
              <el-icon size="32"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ conversionRate }}%</div>
              <div class="stat-label">转化率</div>
              <div class="stat-trend" :class="conversionTrend >= 0 ? 'up' : 'down'">
                <el-icon>{{ conversionTrend >= 0 ? 'CaretTop' : 'CaretBottom' }}</el-icon>
                <span>{{ Math.abs(conversionTrend) }}%</span>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <div class="common-card">
          <div class="card-header">
            <h3>最近7天通话趋势</h3>
            <el-button type="text" @click="$router.push('/report/call-trend')">查看全部</el-button>
          </div>
          <div ref="callTrendChart" style="height: 350px;"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="common-card">
          <div class="card-header">
            <h3>坐席绩效排名</h3>
            <el-button type="text" @click="$router.push('/report/agent-performance')">查看全部</el-button>
          </div>
          <el-table :data="agentRankList" border stripe>
            <el-table-column prop="rank" label="排名" width="80" align="center">
              <template #default="scope">
                <el-tag :type="scope.row.rank <= 3 ? 'warning' : 'info'" size="small">
                  {{ scope.row.rank }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="agent_name" label="坐席姓名" />
            <el-table-column prop="call_count" label="通话次数" width="100" align="center" />
            <el-table-column prop="total_duration" label="总时长" width="120" align="center">
              <template #default="scope">
                {{ formatDuration(scope.row.total_duration) }}
              </template>
            </el-table-column>
            <el-table-column prop="conversion_rate" label="转化率" width="100" align="center">
              <template #default="scope">
                {{ scope.row.conversion_rate }}%
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="8">
        <div class="common-card">
          <div class="card-header">
            <h3>通话状态分布</h3>
          </div>
          <div ref="callStatusChart" style="height: 300px;"></div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="common-card">
          <div class="card-header">
            <h3>客户来源分布</h3>
            <el-button type="text" @click="$router.push('/report/customer-analysis')">查看全部</el-button>
          </div>
          <div ref="sourceChart" style="height: 300px;"></div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="common-card">
          <div class="card-header">
            <h3>客户等级分布</h3>
            <el-button type="text" @click="$router.push('/report/customer-analysis')">查看全部</el-button>
          </div>
          <div ref="levelChart" style="height: 300px;"></div>
        </div>
      </el-col>
    </el-row>

    <div class="common-card mt-20">
      <div class="card-header">
        <h3>最近通话记录</h3>
        <el-button type="text" @click="$router.push('/call/record')">查看全部</el-button>
      </div>
      <el-table :data="recentCallList" border stripe v-loading="loading">
        <el-table-column prop="caller" label="主叫号码" width="130" />
        <el-table-column prop="called" label="被叫号码" width="130" />
        <el-table-column prop="direction" label="呼叫方向" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.direction === 1 ? 'primary' : 'success'" size="small">
              {{ scope.row.direction === 1 ? '外呼' : '呼入' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="通话状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)" size="small">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="通话时长" width="100" align="center">
          <template #default="scope">
            {{ scope.row.duration ? formatDuration(scope.row.duration) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="user_name" label="坐席" width="100" />
        <el-table-column prop="customer_name" label="客户名称" width="120" show-overflow-tooltip />
        <el-table-column prop="start_time" label="呼叫时间" width="160" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { Phone, Check, Timer, TrendCharts, CaretTop, CaretBottom } from '@element-plus/icons-vue'
import { getCallStatisticsApi, getCallRecordListApi } from '@/api/call'
import { formatDuration } from '@/utils/datetime'

const loading = ref(false)
const callTrendChart = ref(null)
const callStatusChart = ref(null)
const sourceChart = ref(null)
const levelChart = ref(null)

// 统计数据
const totalCalls = ref(0)
const answerRate = ref(0)
const avgDuration = ref('00:00')
const conversionRate = ref(0)

const callTrend = ref(0)
const answerRateTrend = ref(0)
const durationTrend = ref(0)
const conversionTrend = ref(0)

const agentRankList = ref([])
const recentCallList = ref([])

// 获取统计数据
const getStatistics = async () => {
  try {
    const res = await getCallStatisticsApi({ period: '7d' })
    const data = res.data

    totalCalls.value = data.total_calls || 0
    answerRate.value = data.answer_rate || 0
    avgDuration.value = formatDuration(data.avg_duration || 0)
    conversionRate.value = data.conversion_rate || 0

    callTrend.value = data.call_trend || 0
    answerRateTrend.value = data.answer_rate_trend || 0
    durationTrend.value = data.duration_trend || 0
    conversionTrend.value = data.conversion_trend || 0

    agentRankList.value = data.agent_rank || []
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  }
}

// 获取最近通话记录
const getRecentCalls = async () => {
  loading.value = true
  try {
    const res = await getCallRecordListApi({ page: 1, page_size: 10 })
    recentCallList.value = res.data.list || []
  } catch (error) {
    ElMessage.error('获取通话记录失败')
  } finally {
    loading.value = false
  }
}

// 初始化通话趋势图表
const initCallTrendChart = () => {
  if (!callTrendChart.value) return

  const chart = echarts.init(callTrendChart.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    legend: {
      data: ['通话次数', '接通率']
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['5/7', '5/8', '5/9', '5/10', '5/11', '5/12', '5/13']
    },
    yAxis: [
      {
        type: 'value',
        name: '通话次数',
        position: 'left'
      },
      {
        type: 'value',
        name: '接通率',
        position: 'right',
        axisLabel: {
          formatter: '{value}%'
        }
      }
    ],
    series: [
      {
        name: '通话次数',
        type: 'line',
        smooth: true,
        data: [120, 132, 101, 134, 90, 230, 210],
        itemStyle: {
          color: '#409eff'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.5)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
          ])
        }
      },
      {
        name: '接通率',
        type: 'line',
        smooth: true,
        yAxisIndex: 1,
        data: [85, 78, 92, 88, 95, 82, 89],
        itemStyle: {
          color: '#67c23a'
        }
      }
    ]
  }

  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

// 初始化通话状态分布图表
const initCallStatusChart = () => {
  if (!callStatusChart.value) return

  const chart = echarts.init(callStatusChart.value)
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '通话状态',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '16',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: 735, name: '已接通', itemStyle: { color: '#67c23a' } },
          { value: 210, name: '未接通', itemStyle: { color: '#f56c6c' } },
          { value: 134, name: '用户拒接', itemStyle: { color: '#e6a23c' } },
          { value: 48, name: '忙线', itemStyle: { color: '#909399' } }
        ]
      }
    ]
  }

  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

// 初始化客户来源分布图表
const initSourceChart = () => {
  if (!sourceChart.value) return

  const chart = echarts.init(sourceChart.value)
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '客户来源',
        type: 'pie',
        radius: '50%',
        data: [
          { value: 335, name: '网站注册', itemStyle: { color: '#409eff' } },
          { value: 310, name: '线上推广', itemStyle: { color: '#67c23a' } },
          { value: 234, name: '朋友介绍', itemStyle: { color: '#e6a23c' } },
          { value: 135, name: '线下活动', itemStyle: { color: '#f56c6c' } },
          { value: 148, name: '其他', itemStyle: { color: '#909399' } }
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

// 初始化客户等级分布图表
const initLevelChart = () => {
  if (!levelChart.value) return

  const chart = echarts.init(levelChart.value)
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '客户等级',
        type: 'pie',
        radius: '50%',
        data: [
          { value: 635, name: '普通客户', itemStyle: { color: '#909399' } },
          { value: 210, name: 'VIP客户', itemStyle: { color: '#e6a23c' } },
          { value: 134, name: '重要客户', itemStyle: { color: '#f56c6c' } }
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

// 获取状态标签类型
const getStatusTagType = (status) => {
  const typeMap = {
    1: 'info',
    2: 'success',
    3: 'danger',
    4: 'warning',
    5: 'default'
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const textMap = {
    1: '未接通',
    2: '已接通',
    3: '已拒绝',
    4: '忙线',
    5: '已取消'
  }
  return textMap[status] || '未知'
}

onMounted(() => {
  getStatistics()
  getRecentCalls()
  setTimeout(() => {
    initCallTrendChart()
    initCallStatusChart()
    initSourceChart()
    initLevelChart()
  }, 100)
})

onUnmounted(() => {
  window.removeEventListener('resize', () => {})
})
</script>

<style lang="scss" scoped>
.report-container {
  .stat-card {
    display: flex;
    align-items: center;
    padding: 20px;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);

    &.total-calls {
      .stat-icon {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }
    }

    &.answer-rate {
      .stat-icon {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      }
    }

    &.avg-duration {
      .stat-icon {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      }
    }

    &.conversion-rate {
      .stat-icon {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
      }
    }

    .stat-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 70px;
      height: 70px;
      border-radius: 50%;
      color: #fff;
      margin-right: 20px;
    }

    .stat-info {
      flex: 1;

      .stat-value {
        font-size: 32px;
        font-weight: bold;
        color: #303133;
        margin-bottom: 5px;
      }

      .stat-label {
        font-size: 14px;
        color: #909399;
        margin-bottom: 5px;
      }

      .stat-trend {
        font-size: 12px;
        display: flex;
        align-items: center;
        gap: 3px;

        &.up {
          color: #67c23a;
        }

        &.down {
          color: #f56c6c;
        }
      }
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;

    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: bold;
    }
  }
}
</style>
