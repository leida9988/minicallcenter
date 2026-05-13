<template>
  <div class="call-trend-report">
    <!-- 搜索区域 -->
    <div class="common-card">
      <el-form :model="queryParams" ref="queryFormRef" :inline="true" label-width="80px">
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 280px"
          />
        </el-form-item>
        <el-form-item label="统计维度">
          <el-select v-model="queryParams.dimension" style="width: 150px">
            <el-option label="按小时" value="hour" />
            <el-option label="按天" value="day" />
            <el-option label="按周" value="week" />
            <el-option label="按月" value="month" />
          </el-select>
        </el-form-item>
        <el-form-item label="坐席">
          <el-select
            v-model="queryParams.user_id"
            placeholder="全部坐席"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="user in userList"
              :key="user.id"
              :label="user.nickname || user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="resetQuery">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
          <el-button type="success" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 统计概览 -->
    <div class="common-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">总通话次数</div>
            <div class="stat-value">{{ statistics.total_calls }}</div>
            <div class="stat-change" :class="statistics.calls_change >= 0 ? 'up' : 'down'">
              <el-icon>{{ statistics.calls_change >= 0 ? 'CaretTop' : 'CaretBottom' }}</el-icon>
              <span>{{ Math.abs(statistics.calls_change) }}%</span>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">接通率</div>
            <div class="stat-value">{{ statistics.answer_rate }}%</div>
            <div class="stat-change" :class="statistics.answer_rate_change >= 0 ? 'up' : 'down'">
              <el-icon>{{ statistics.answer_rate_change >= 0 ? 'CaretTop' : 'CaretBottom' }}</el-icon>
              <span>{{ Math.abs(statistics.answer_rate_change) }}%</span>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">总通话时长</div>
            <div class="stat-value">{{ formatDuration(statistics.total_duration) }}</div>
            <div class="stat-change" :class="statistics.duration_change >= 0 ? 'up' : 'down'">
              <el-icon>{{ statistics.duration_change >= 0 ? 'CaretTop' : 'CaretBottom' }}</el-icon>
              <span>{{ Math.abs(statistics.duration_change) }}%</span>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">平均通话时长</div>
            <div class="stat-value">{{ formatDuration(statistics.avg_duration) }}</div>
            <div class="stat-change" :class="statistics.avg_duration_change >= 0 ? 'up' : 'down'">
              <el-icon>{{ statistics.avg_duration_change >= 0 ? 'CaretTop' : 'CaretBottom' }}</el-icon>
              <span>{{ Math.abs(statistics.avg_duration_change) }}%</span>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 图表区域 -->
    <div class="common-card mt-20">
      <div class="card-header">
        <h3>通话趋势</h3>
        <el-radio-group v-model="chartType" size="small">
          <el-radio-button label="line">折线图</el-radio-button>
          <el-radio-button label="bar">柱状图</el-radio-button>
        </el-radio-group>
      </div>
      <div ref="callTrendChart" style="height: 400px;"></div>
    </div>

    <!-- 细分统计 -->
    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <div class="common-card">
          <div class="card-header">
            <h3>通话时段分布</h3>
          </div>
          <div ref="hourChart" style="height: 350px;"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="common-card">
          <div class="card-header">
            <h3>通话状态分布</h3>
          </div>
          <div ref="statusChart" style="height: 350px;"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 明细数据 -->
    <div class="common-card mt-20">
      <div class="card-header">
        <h3>明细数据</h3>
      </div>
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="date" label="日期" width="150" />
        <el-table-column prop="total_calls" label="总通话次数" width="120" align="center" />
        <el-table-column prop="answer_calls" label="接通次数" width="120" align="center" />
        <el-table-column prop="answer_rate" label="接通率" width="100" align="center">
          <template #default="scope">
            {{ scope.row.answer_rate }}%
          </template>
        </el-table-column>
        <el-table-column prop="total_duration" label="总通话时长" width="150" align="center">
          <template #default="scope">
            {{ formatDuration(scope.row.total_duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="avg_duration" label="平均通话时长" width="150" align="center">
          <template #default="scope">
            {{ formatDuration(scope.row.avg_duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="outbound_count" label="外呼次数" width="120" align="center" />
        <el-table-column prop="inbound_count" label="呼入次数" width="120" align="center" />
      </el-table>
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.page_size"
          :total="total"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleQuery"
          @current-change="handleQuery"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Download, CaretTop, CaretBottom } from '@element-plus/icons-vue'
import { getCallStatisticsApi, exportCallRecordApi } from '@/api/call'
import { getUserListApi } from '@/api/user'
import { formatDuration } from '@/utils/datetime'

const loading = ref(false)
const queryFormRef = ref(null)
const callTrendChart = ref(null)
const hourChart = ref(null)
const statusChart = ref(null)
const userList = ref([])
const tableData = ref([])
const total = ref(0)
const dateRange = ref([])
const chartType = ref('line')

// 查询参数
const queryParams = reactive({
  page: 1,
  page_size: 20,
  dimension: 'day',
  user_id: null,
  start_time: '',
  end_time: ''
})

// 统计数据
const statistics = reactive({
  total_calls: 0,
  answer_rate: 0,
  total_duration: 0,
  avg_duration: 0,
  calls_change: 0,
  answer_rate_change: 0,
  duration_change: 0,
  avg_duration_change: 0
})

// 获取用户列表
const getUserList = async () => {
  try {
    const res = await getUserListApi({ page: 1, page_size: 1000 })
    userList.value = res.data.list
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  }
}

// 获取统计数据
const getStatistics = async () => {
  loading.value = true
  try {
    if (dateRange.value && dateRange.value.length === 2) {
      queryParams.start_time = dateRange.value[0]
      queryParams.end_time = dateRange.value[1]
    } else {
      // 默认最近30天
      const end = new Date()
      const start = new Date(end.getTime() - 30 * 24 * 60 * 60 * 1000)
      queryParams.start_time = start.toISOString().split('T')[0]
      queryParams.end_time = end.toISOString().split('T')[0]
      dateRange.value = [queryParams.start_time, queryParams.end_time]
    }

    const res = await getCallStatisticsApi(queryParams)
    const data = res.data

    Object.assign(statistics, data.overview || {})
    tableData.value = data.details || []
    total.value = data.total || 0

    // 更新图表
    updateCharts(data.chart_data || {})
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value = false
  }
}

// 更新图表
const updateCharts = (chartData) => {
  // 使用模拟数据
  const dates = chartData.dates || ['5/1', '5/2', '5/3', '5/4', '5/5', '5/6', '5/7', '5/8', '5/9', '5/10', '5/11', '5/12', '5/13']
  const callCounts = chartData.call_counts || [120, 132, 101, 134, 90, 230, 210, 180, 156, 198, 170, 220, 250]
  const answerRates = chartData.answer_rates || [85, 78, 92, 88, 95, 82, 89, 87, 91, 84, 90, 86, 88]

  // 更新通话趋势图表
  if (callTrendChart.value) {
    const chart = echarts.getInstanceByDom(callTrendChart.value) || echarts.init(callTrendChart.value)
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
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: dates
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
          type: chartType.value,
          smooth: chartType.value === 'line',
          data: callCounts,
          itemStyle: {
            color: '#409eff'
          },
          areaStyle: chartType.value === 'line' ? {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(64, 158, 255, 0.5)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
            ])
          } : undefined
        },
        {
          name: '接通率',
          type: 'line',
          smooth: true,
          yAxisIndex: 1,
          data: answerRates,
          itemStyle: {
            color: '#67c23a'
          }
        }
      ]
    }
    chart.setOption(option)
  }

  // 更新时段分布图表
  if (hourChart.value) {
    const chart = echarts.getInstanceByDom(hourChart.value) || echarts.init(hourChart.value)
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
        type: 'category',
        data: ['0点', '1点', '2点', '3点', '4点', '5点', '6点', '7点', '8点', '9点', '10点', '11点', '12点', '13点', '14点', '15点', '16点', '17点', '18点', '19点', '20点', '21点', '22点', '23点']
      },
      yAxis: {
        type: 'value',
        name: '通话次数'
      },
      series: [
        {
          name: '通话次数',
          type: 'bar',
          data: [10, 5, 3, 2, 1, 5, 15, 30, 60, 85, 90, 75, 60, 80, 95, 100, 90, 70, 50, 45, 40, 30, 20, 15],
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#83bff6' },
              { offset: 0.5, color: '#188df0' },
              { offset: 1, color: '#188df0' }
            ])
          }
        }
      ]
    }
    chart.setOption(option)
  }

  // 更新状态分布图表
  if (statusChart.value) {
    const chart = echarts.getInstanceByDom(statusChart.value) || echarts.init(statusChart.value)
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
            show: true,
            formatter: '{b}: {d}%'
          },
          data: [
            { value: 2350, name: '已接通', itemStyle: { color: '#67c23a' } },
            { value: 610, name: '未接通', itemStyle: { color: '#f56c6c' } },
            { value: 334, name: '用户拒接', itemStyle: { color: '#e6a23c' } },
            { value: 148, name: '忙线', itemStyle: { color: '#909399' } },
            { value: 120, name: '取消', itemStyle: { color: '#409eff' } }
          ]
        }
      ]
    }
    chart.setOption(option)
  }
}

// 查询
const handleQuery = () => {
  queryParams.page = 1
  getStatistics()
}

// 重置
const resetQuery = () => {
  queryFormRef.value?.resetFields()
  dateRange.value = []
  handleQuery()
}

// 导出
const handleExport = () => {
  ElMessage.info('导出功能开发中')
}

// 监听图表类型变化
watch(chartType, () => {
  updateCharts({})
})

onMounted(() => {
  getUserList()
  getStatistics()

  window.addEventListener('resize', () => {
    if (callTrendChart.value) {
      const chart = echarts.getInstanceByDom(callTrendChart.value)
      chart?.resize()
    }
    if (hourChart.value) {
      const chart = echarts.getInstanceByDom(hourChart.value)
      chart?.resize()
    }
    if (statusChart.value) {
      const chart = echarts.getInstanceByDom(statusChart.value)
      chart?.resize()
    }
  })
})
</script>

<style lang="scss" scoped>
.call-trend-report {
  .stat-item {
    text-align: center;
    padding: 20px;
    background: #f5f7fa;
    border-radius: 8px;

    .stat-label {
      font-size: 14px;
      color: #909399;
      margin-bottom: 10px;
    }

    .stat-value {
      font-size: 32px;
      font-weight: bold;
      color: #303133;
      margin-bottom: 10px;
    }

    .stat-change {
      font-size: 12px;
      display: inline-flex;
      align-items: center;
      gap: 3px;
      padding: 2px 8px;
      border-radius: 4px;

      &.up {
        color: #67c23a;
        background: rgba(103, 194, 58, 0.1);
      }

      &.down {
        color: #f56c6c;
        background: rgba(245, 108, 108, 0.1);
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
