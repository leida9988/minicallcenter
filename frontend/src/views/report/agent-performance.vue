<template>
  <div class="agent-performance-report">
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
        <el-form-item label="部门">
          <el-select
            v-model="queryParams.department_id"
            placeholder="全部部门"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="dept in departmentList"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
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

    <!-- 整体统计 -->
    <div class="common-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">坐席总数</div>
            <div class="stat-value">{{ statistics.total_agents }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">平均通话次数</div>
            <div class="stat-value">{{ statistics.avg_calls_per_agent }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">平均通话时长</div>
            <div class="stat-value">{{ formatDuration(statistics.avg_duration_per_agent) }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">平均转化率</div>
            <div class="stat-value">{{ statistics.avg_conversion_rate }}%</div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 排名图表 -->
    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <div class="common-card">
          <div class="card-header">
            <h3>通话次数排名</h3>
            <el-button type="text" @click="sortBy('call_count')">
              {{ sortField === 'call_count' ? (sortOrder === 'desc' ? '↓ 降序' : '↑ 升序') : '排序' }}
            </el-button>
          </div>
          <div ref="callCountChart" style="height: 350px;"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="common-card">
          <div class="card-header">
            <h3>通话时长排名</h3>
            <el-button type="text" @click="sortBy('total_duration')">
              {{ sortField === 'total_duration' ? (sortOrder === 'desc' ? '↓ 降序' : '↑ 升序') : '排序' }}
            </el-button>
          </div>
          <div ref="callDurationChart" style="height: 350px;"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <div class="common-card">
          <div class="card-header">
            <h3>接通率排名</h3>
            <el-button type="text" @click="sortBy('answer_rate')">
              {{ sortField === 'answer_rate' ? (sortOrder === 'desc' ? '↓ 降序' : '↑ 升序') : '排序' }}
            </el-button>
          </div>
          <div ref="answerRateChart" style="height: 350px;"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="common-card">
          <div class="card-header">
            <h3>转化率排名</h3>
            <el-button type="text" @click="sortBy('conversion_rate')">
              {{ sortField === 'conversion_rate' ? (sortOrder === 'desc' ? '↓ 降序' : '↑ 升序') : '排序' }}
            </el-button>
          </div>
          <div ref="conversionRateChart" style="height: 350px;"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 详细数据表格 -->
    <div class="common-card mt-20">
      <div class="card-header">
        <h3>绩效明细</h3>
      </div>
      <el-table :data="tableData" border stripe v-loading="loading" :default-sort="{ prop: sortField, order: sortOrder === 'desc' ? 'descending' : 'ascending' }" @sort-change="handleSortChange">
        <el-table-column prop="rank" label="排名" width="80" align="center" sortable>
          <template #default="scope">
            <el-tag :type="scope.row.rank <= 3 ? 'warning' : 'info'" size="small">
              {{ scope.row.rank }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="agent_name" label="坐席姓名" width="120" sortable />
        <el-table-column prop="department" label="所属部门" width="120" />
        <el-table-column prop="call_count" label="通话次数" width="120" align="center" sortable />
        <el-table-column prop="answer_count" label="接通次数" width="120" align="center" />
        <el-table-column prop="answer_rate" label="接通率" width="100" align="center" sortable>
          <template #default="scope">
            <el-progress :percentage="scope.row.answer_rate" :show-text="true" :stroke-width="10" />
          </template>
        </el-table-column>
        <el-table-column prop="total_duration" label="总通话时长" width="150" align="center" sortable>
          <template #default="scope">
            {{ formatDuration(scope.row.total_duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="avg_duration" label="平均通话时长" width="150" align="center">
          <template #default="scope">
            {{ formatDuration(scope.row.avg_duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="follow_count" label="跟进次数" width="120" align="center" />
        <el-table-column prop="conversion_count" label="转化客户数" width="120" align="center" />
        <el-table-column prop="conversion_rate" label="转化率" width="100" align="center" sortable>
          <template #default="scope">
            <el-progress :percentage="scope.row.conversion_rate" :show-text="true" :stroke-width="10" color="#67c23a" />
          </template>
        </el-table-column>
        <el-table-column prop="score" label="综合评分" width="100" align="center" sortable>
          <template #default="scope">
            <el-tag :type="getScoreTagType(scope.row.score)" size="small">
              {{ scope.row.score }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button type="primary" text size="small" @click="viewDetail(scope.row)">
              详情
            </el-button>
          </template>
        </el-table-column>
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

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="坐席绩效详情" width="900px">
      <div v-if="currentAgent" class="agent-detail">
        <div class="agent-info">
          <el-avatar :size="80" class="agent-avatar">
            {{ currentAgent.agent_name.charAt(0) }}
          </el-avatar>
          <div class="info-text">
            <h3>{{ currentAgent.agent_name }}</h3>
            <p>部门：{{ currentAgent.department }}</p>
            <p>入职时间：{{ currentAgent.hire_date }}</p>
            <p>综合评分：<el-tag :type="getScoreTagType(currentAgent.score)" size="large">{{ currentAgent.score }}</el-tag></p>
          </div>
        </div>

        <el-descriptions :column="2" border class="mt-20">
          <el-descriptions-item label="通话次数">{{ currentAgent.call_count }} 次</el-descriptions-item>
          <el-descriptions-item label="接通次数">{{ currentAgent.answer_count }} 次</el-descriptions-item>
          <el-descriptions-item label="接通率">{{ currentAgent.answer_rate }}%</el-descriptions-item>
          <el-descriptions-item label="总通话时长">{{ formatDuration(currentAgent.total_duration) }}</el-descriptions-item>
          <el-descriptions-item label="平均通话时长">{{ formatDuration(currentAgent.avg_duration) }}</el-descriptions-item>
          <el-descriptions-item label="跟进次数">{{ currentAgent.follow_count }} 次</el-descriptions-item>
          <el-descriptions-item label="转化客户数">{{ currentAgent.conversion_count }} 个</el-descriptions-item>
          <el-descriptions-item label="转化率">{{ currentAgent.conversion_rate }}%</el-descriptions-item>
        </el-descriptions>

        <div class="mt-20">
          <h4>每日绩效趋势</h4>
          <div ref="trendChart" style="height: 300px; margin-top: 15px;"></div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Download } from '@element-plus/icons-vue'
import { getCallStatisticsApi } from '@/api/call'
import { getUserListApi } from '@/api/user'
import { formatDuration } from '@/utils/datetime'

const loading = ref(false)
const queryFormRef = ref(null)
const callCountChart = ref(null)
const callDurationChart = ref(null)
const answerRateChart = ref(null)
const conversionRateChart = ref(null)
const trendChart = ref(null)
const departmentList = ref([])
const userList = ref([])
const tableData = ref([])
const total = ref(0)
const dateRange = ref([])
const detailVisible = ref(false)
const currentAgent = ref(null)
const sortField = ref('call_count')
const sortOrder = ref('desc')

// 查询参数
const queryParams = reactive({
  page: 1,
  page_size: 20,
  department_id: null,
  user_id: null,
  start_time: '',
  end_time: ''
})

// 统计数据
const statistics = reactive({
  total_agents: 0,
  avg_calls_per_agent: 0,
  avg_duration_per_agent: 0,
  avg_conversion_rate: 0
})

// 获取部门列表
const getDepartmentList = async () => {
  // 模拟数据
  departmentList.value = [
    { id: 1, name: '销售一部' },
    { id: 2, name: '销售二部' },
    { id: 3, name: '销售三部' },
    { id: 4, name: '客服部' }
  ]
}

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
      // 默认本月
      const now = new Date()
      const start = new Date(now.getFullYear(), now.getMonth(), 1)
      queryParams.start_time = start.toISOString().split('T')[0]
      queryParams.end_time = now.toISOString().split('T')[0]
      dateRange.value = [queryParams.start_time, queryParams.end_time]
    }

    const res = await getCallStatisticsApi({ ...queryParams, type: 'agent' })
    const data = res.data

    Object.assign(statistics, data.overview || {})
    tableData.value = data.details || []
    total.value = data.total || 0

    // 更新图表
    updateCharts(data.details || [])
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value = false
  }
}

// 更新图表
const updateCharts = (data) => {
  // 排序数据
  const sortedByCalls = [...data].sort((a, b) => b.call_count - a.call_count).slice(0, 10)
  const sortedByDuration = [...data].sort((a, b) => b.total_duration - a.total_duration).slice(0, 10)
  const sortedByAnswerRate = [...data].sort((a, b) => b.answer_rate - a.answer_rate).slice(0, 10)
  const sortedByConversion = [...data].sort((a, b) => b.conversion_rate - a.conversion_rate).slice(0, 10)

  // 通话次数排名
  if (callCountChart.value) {
    const chart = echarts.getInstanceByDom(callCountChart.value) || echarts.init(callCountChart.value)
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
        name: '通话次数'
      },
      yAxis: {
        type: 'category',
        data: sortedByCalls.map(item => item.agent_name),
        inverse: true
      },
      series: [
        {
          name: '通话次数',
          type: 'bar',
          data: sortedByCalls.map(item => item.call_count),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#83bff6' },
              { offset: 0.5, color: '#188df0' },
              { offset: 1, color: '#188df0' }
            ])
          },
          label: {
            show: true,
            position: 'right'
          }
        }
      ]
    }
    chart.setOption(option)
  }

  // 通话时长排名
  if (callDurationChart.value) {
    const chart = echarts.getInstanceByDom(callDurationChart.value) || echarts.init(callDurationChart.value)
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
        name: '通话时长(分钟)'
      },
      yAxis: {
        type: 'category',
        data: sortedByDuration.map(item => item.agent_name),
        inverse: true
      },
      series: [
        {
          name: '通话时长',
          type: 'bar',
          data: sortedByDuration.map(item => Math.round(item.total_duration / 60)),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#80d091' },
              { offset: 0.5, color: '#67c23a' },
              { offset: 1, color: '#67c23a' }
            ])
          },
          label: {
            show: true,
            position: 'right',
            formatter: '{value}m'
          }
        }
      ]
    }
    chart.setOption(option)
  }

  // 接通率排名
  if (answerRateChart.value) {
    const chart = echarts.getInstanceByDom(answerRateChart.value) || echarts.init(answerRateChart.value)
    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: '{b}: {c}%'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'value',
        name: '接通率',
        max: 100,
        axisLabel: {
          formatter: '{value}%'
        }
      },
      yAxis: {
        type: 'category',
        data: sortedByAnswerRate.map(item => item.agent_name),
        inverse: true
      },
      series: [
        {
          name: '接通率',
          type: 'bar',
          data: sortedByAnswerRate.map(item => item.answer_rate),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#f7d376' },
              { offset: 0.5, color: '#e6a23c' },
              { offset: 1, color: '#e6a23c' }
            ])
          },
          label: {
            show: true,
            position: 'right',
            formatter: '{value}%'
          }
        }
      ]
    }
    chart.setOption(option)
  }

  // 转化率排名
  if (conversionRateChart.value) {
    const chart = echarts.getInstanceByDom(conversionRateChart.value) || echarts.init(conversionRateChart.value)
    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: '{b}: {c}%'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'value',
        name: '转化率',
        max: 100,
        axisLabel: {
          formatter: '{value}%'
        }
      },
      yAxis: {
        type: 'category',
        data: sortedByConversion.map(item => item.agent_name),
        inverse: true
      },
      series: [
        {
          name: '转化率',
          type: 'bar',
          data: sortedByConversion.map(item => item.conversion_rate),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#f49c9c' },
              { offset: 0.5, color: '#f56c6c' },
              { offset: 1, color: '#f56c6c' }
            ])
          },
          label: {
            show: true,
            position: 'right',
            formatter: '{value}%'
          }
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

// 排序
const sortBy = (field) => {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'desc' ? 'asc' : 'desc'
  } else {
    sortField.value = field
    sortOrder.value = 'desc'
  }
  handleQuery()
}

// 表格排序变化
const handleSortChange = (sortInfo) => {
  sortField.value = sortInfo.prop
  sortOrder.value = sortInfo.order === 'descending' ? 'desc' : 'asc'
  handleQuery()
}

// 获取评分标签类型
const getScoreTagType = (score) => {
  if (score >= 90) return 'success'
  if (score >= 80) return 'warning'
  if (score >= 60) return 'info'
  return 'danger'
}

// 查看详情
const viewDetail = (row) => {
  currentAgent.value = {
    ...row,
    hire_date: '2023-01-15'
  }
  detailVisible.value = true

  setTimeout(() => {
    if (trendChart.value) {
      const chart = echarts.getInstanceByDom(trendChart.value) || echarts.init(trendChart.value)
      const option = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['通话次数', '转化率']
        },
        xAxis: {
          type: 'category',
          data: ['5/1', '5/2', '5/3', '5/4', '5/5', '5/6', '5/7', '5/8', '5/9', '5/10', '5/11', '5/12', '5/13']
        },
        yAxis: [
          {
            type: 'value',
            name: '通话次数',
            position: 'left'
          },
          {
            type: 'value',
            name: '转化率',
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
            data: [20, 25, 18, 22, 28, 30, 26, 24, 32, 35, 29, 31, 33],
            itemStyle: {
              color: '#409eff'
            }
          },
          {
            name: '转化率',
            type: 'line',
            smooth: true,
            yAxisIndex: 1,
            data: [15, 18, 12, 20, 22, 25, 23, 19, 26, 28, 24, 27, 29],
            itemStyle: {
              color: '#67c23a'
            }
          }
        ]
      }
      chart.setOption(option)
    }
  }, 100)
}

onMounted(() => {
  getDepartmentList()
  getUserList()
  getStatistics()

  window.addEventListener('resize', () => {
    const charts = [callCountChart, callDurationChart, answerRateChart, conversionRateChart, trendChart]
    charts.forEach(chartRef => {
      if (chartRef.value) {
        const chart = echarts.getInstanceByDom(chartRef.value)
        chart?.resize()
      }
    })
  })
})
</script>

<style lang="scss" scoped>
.agent-performance-report {
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

  .agent-detail {
    .agent-info {
      display: flex;
      align-items: center;
      gap: 20px;

      .agent-avatar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
        font-size: 32px;
        font-weight: bold;
      }

      .info-text {
        h3 {
          margin: 0 0 10px 0;
          font-size: 20px;
          font-weight: bold;
        }

        p {
          margin: 0 0 5px 0;
          color: #606266;
        }
      }
    }
  }
}
</style>
