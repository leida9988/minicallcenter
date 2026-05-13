<template>
  <div class="customer-analysis-report">
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
        <el-form-item label="客户等级">
          <el-select
            v-model="queryParams.level"
            placeholder="全部等级"
            clearable
            style="width: 150px"
          >
            <el-option label="普通" :value="1" />
            <el-option label="VIP" :value="2" />
            <el-option label="重要客户" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="客户状态">
          <el-select
            v-model="queryParams.status"
            placeholder="全部状态"
            clearable
            style="width: 150px"
          >
            <el-option label="待联系" :value="1" />
            <el-option label="联系中" :value="2" />
            <el-option label="有意向" :value="3" />
            <el-option label="已成交" :value="4" />
            <el-option label="已拒绝" :value="5" />
            <el-option label="无效客户" :value="6" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属坐席">
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
            <div class="stat-label">客户总数</div>
            <div class="stat-value">{{ statistics.total_customers }}</div>
            <div class="stat-change" :class="statistics.customer_growth >= 0 ? 'up' : 'down'">
              <el-icon>{{ statistics.customer_growth >= 0 ? 'CaretTop' : 'CaretBottom' }}</el-icon>
              <span>{{ Math.abs(statistics.customer_growth) }}%</span>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">新增客户</div>
            <div class="stat-value">{{ statistics.new_customers }}</div>
            <div class="stat-change" :class="statistics.new_growth >= 0 ? 'up' : 'down'">
              <el-icon>{{ statistics.new_growth >= 0 ? 'CaretTop' : 'CaretBottom' }}</el-icon>
              <span>{{ Math.abs(statistics.new_growth) }}%</span>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">转化率</div>
            <div class="stat-value">{{ statistics.conversion_rate }}%</div>
            <div class="stat-change" :class="statistics.conversion_growth >= 0 ? 'up' : 'down'">
              <el-icon>{{ statistics.conversion_growth >= 0 ? 'CaretTop' : 'CaretBottom' }}</el-icon>
              <span>{{ Math.abs(statistics.conversion_growth) }}%</span>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-label">客户跟进率</div>
            <div class="stat-value">{{ statistics.follow_rate }}%</div>
            <div class="stat-change" :class="statistics.follow_growth >= 0 ? 'up' : 'down'">
              <el-icon>{{ statistics.follow_growth >= 0 ? 'CaretTop' : 'CaretBottom' }}</el-icon>
              <span>{{ Math.abs(statistics.follow_growth) }}%</span>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 分布统计 -->
    <el-row :gutter="20" class="mt-20">
      <el-col :span="8">
        <div class="common-card">
          <div class="card-header">
            <h3>客户等级分布</h3>
          </div>
          <div ref="levelChart" style="height: 320px;"></div>
          <div class="chart-legend">
            <div class="legend-item">
              <span class="legend-color" style="background: #909399;"></span>
              <span class="legend-text">普通客户</span>
              <span class="legend-count">{{ statistics.level_breakdown?.[0]?.count || 0 }}</span>
              <span class="legend-percent">{{ statistics.level_breakdown?.[0]?.percent || 0 }}%</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background: #e6a23c;"></span>
              <span class="legend-text">VIP客户</span>
              <span class="legend-count">{{ statistics.level_breakdown?.[1]?.count || 0 }}</span>
              <span class="legend-percent">{{ statistics.level_breakdown?.[1]?.percent || 0 }}%</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background: #f56c6c;"></span>
              <span class="legend-text">重要客户</span>
              <span class="legend-count">{{ statistics.level_breakdown?.[2]?.count || 0 }}</span>
              <span class="legend-percent">{{ statistics.level_breakdown?.[2]?.percent || 0 }}%</span>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="common-card">
          <div class="card-header">
            <h3>客户状态分布</h3>
          </div>
          <div ref="statusChart" style="height: 320px;"></div>
          <div class="chart-legend" style="grid-template-columns: repeat(2, 1fr);">
            <div class="legend-item">
              <span class="legend-color" style="background: #909399;"></span>
              <span class="legend-text">待联系</span>
              <span class="legend-count">{{ statistics.status_breakdown?.[0]?.count || 0 }}</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background: #409eff;"></span>
              <span class="legend-text">联系中</span>
              <span class="legend-count">{{ statistics.status_breakdown?.[1]?.count || 0 }}</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background: #67c23a;"></span>
              <span class="legend-text">有意向</span>
              <span class="legend-count">{{ statistics.status_breakdown?.[2]?.count || 0 }}</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background: #f56c6c;"></span>
              <span class="legend-text">已成交</span>
              <span class="legend-count">{{ statistics.status_breakdown?.[3]?.count || 0 }}</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background: #e6a23c;"></span>
              <span class="legend-text">已拒绝</span>
              <span class="legend-count">{{ statistics.status_breakdown?.[4]?.count || 0 }}</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background: #f0f2f5;"></span>
              <span class="legend-text">无效客户</span>
              <span class="legend-count">{{ statistics.status_breakdown?.[5]?.count || 0 }}</span>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="common-card">
          <div class="card-header">
            <h3>客户来源分布</h3>
          </div>
          <div ref="sourceChart" style="height: 320px;"></div>
          <div class="chart-legend" style="grid-template-columns: repeat(2, 1fr);">
            <div class="legend-item">
              <span class="legend-color" style="background: #409eff;"></span>
              <span class="legend-text">网站注册</span>
              <span class="legend-count">{{ statistics.source_breakdown?.[0]?.count || 0 }}</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background: #67c23a;"></span>
              <span class="legend-text">线上推广</span>
              <span class="legend-count">{{ statistics.source_breakdown?.[1]?.count || 0 }}</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background: #e6a23c;"></span>
              <span class="legend-text">朋友介绍</span>
              <span class="legend-count">{{ statistics.source_breakdown?.[2]?.count || 0 }}</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background: #f56c6c;"></span>
              <span class="legend-text">线下活动</span>
              <span class="legend-count">{{ statistics.source_breakdown?.[3]?.count || 0 }}</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background: #909399;"></span>
              <span class="legend-text">其他</span>
              <span class="legend-count">{{ statistics.source_breakdown?.[4]?.count || 0 }}</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 增长趋势 -->
    <div class="common-card mt-20">
      <div class="card-header">
        <h3>客户增长趋势</h3>
      </div>
      <div ref="growthChart" style="height: 400px;"></div>
    </div>

    <!-- 转化漏斗 -->
    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <div class="common-card">
          <div class="card-header">
            <h3>销售转化漏斗</h3>
          </div>
          <div ref="funnelChart" style="height: 400px;"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="common-card">
          <div class="card-header">
            <h3>坐席客户数排名</h3>
          </div>
          <el-table :data="agentRanking" border stripe height="400">
            <el-table-column prop="rank" label="排名" width="80" align="center">
              <template #default="scope">
                <el-tag :type="scope.row.rank <= 3 ? 'warning' : 'info'" size="small">
                  {{ scope.row.rank }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="agent_name" label="坐席姓名" width="120" />
            <el-table-column prop="customer_count" label="客户总数" width="120" align="center" />
            <el-table-column prop="new_customer" label="新增客户" width="120" align="center" />
            <el-table-column prop="conversion_rate" label="转化率" width="100" align="center">
              <template #default="scope">
                {{ scope.row.conversion_rate }}%
              </template>
            </el-table-column>
            <el-table-column prop="avg_follow" label="平均跟进次数" width="130" align="center" />
          </el-table>
        </div>
      </el-col>
    </el-row>

    <!-- 客户标签统计 -->
    <div class="common-card mt-20">
      <div class="card-header">
        <h3>客户标签分布</h3>
      </div>
      <div class="tag-cloud">
        <div
          v-for="tag in tagStatistics"
          :key="tag.id"
          class="tag-item"
          :style="{
            fontSize: `${12 + (tag.count / maxTagCount) * 12}px`,
            color: tag.color,
            backgroundColor: `${tag.color}20`
          }"
        >
          {{ tag.name }} <span class="tag-count">({{ tag.count }})</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Download, CaretTop, CaretBottom } from '@element-plus/icons-vue'
import { getCallStatisticsApi } from '@/api/call'
import { getUserListApi } from '@/api/user'

const loading = ref(false)
const queryFormRef = ref(null)
const levelChart = ref(null)
const statusChart = ref(null)
const sourceChart = ref(null)
const growthChart = ref(null)
const funnelChart = ref(null)
const userList = ref([])
const dateRange = ref([])

// 查询参数
const queryParams = reactive({
  page: 1,
  page_size: 20,
  level: null,
  status: null,
  user_id: null,
  start_time: '',
  end_time: ''
})

// 统计数据
const statistics = reactive({
  total_customers: 0,
  customer_growth: 0,
  new_customers: 0,
  new_growth: 0,
  conversion_rate: 0,
  conversion_growth: 0,
  follow_rate: 0,
  follow_growth: 0,
  level_breakdown: [
    { count: 1200, percent: 60 },
    { count: 500, percent: 25 },
    { count: 300, percent: 15 }
  ],
  status_breakdown: [
    { count: 300, percent: 15 },
    { count: 400, percent: 20 },
    { count: 350, percent: 17.5 },
    { count: 200, percent: 10 },
    { count: 150, percent: 7.5 },
    { count: 600, percent: 30 }
  ],
  source_breakdown: [
    { count: 500, percent: 25 },
    { count: 600, percent: 30 },
    { count: 300, percent: 15 },
    { count: 250, percent: 12.5 },
    { count: 350, percent: 17.5 }
  ]
})

const agentRanking = ref([
  { rank: 1, agent_name: '张三', customer_count: 120, new_customer: 35, conversion_rate: 28, avg_follow: 5.2 },
  { rank: 2, agent_name: '李四', customer_count: 115, new_customer: 32, conversion_rate: 25, avg_follow: 4.8 },
  { rank: 3, agent_name: '王五', customer_count: 110, new_customer: 28, conversion_rate: 30, avg_follow: 5.5 },
  { rank: 4, agent_name: '赵六', customer_count: 105, new_customer: 30, conversion_rate: 22, avg_follow: 4.5 },
  { rank: 5, agent_name: '钱七', customer_count: 100, new_customer: 25, conversion_rate: 26, avg_follow: 5.0 },
  { rank: 6, agent_name: '孙八', customer_count: 95, new_customer: 22, conversion_rate: 24, avg_follow: 4.7 },
  { rank: 7, agent_name: '周九', customer_count: 90, new_customer: 20, conversion_rate: 21, avg_follow: 4.3 },
  { rank: 8, agent_name: '吴十', customer_count: 85, new_customer: 18, conversion_rate: 27, avg_follow: 5.1 }
])

const tagStatistics = ref([
  { id: 1, name: '高意向', count: 320, color: '#f56c6c' },
  { id: 2, name: '已成交', count: 280, color: '#67c23a' },
  { id: 3, name: '需要跟进', count: 250, color: '#e6a23c' },
  { id: 4, name: '价格敏感', count: 200, color: '#409eff' },
  { id: 5, name: '大客户', count: 180, color: '#909399' },
  { id: 6, name: '长期合作', count: 150, color: '#67c23a' },
  { id: 7, name: '待回访', count: 140, color: '#f56c6c' },
  { id: 8, name: '需求明确', count: 130, color: '#409eff' },
  { id: 9, name: '考虑中', count: 120, color: '#e6a23c' },
  { id: 10, name: '已拒绝', count: 100, color: '#909399' },
  { id: 11, name: '优质客户', count: 90, color: '#67c23a' },
  { id: 12, name: '潜在客户', count: 85, color: '#409eff' },
  { id: 13, name: '新客户', count: 80, color: '#e6a23c' },
  { id: 14, name: '老客户', count: 75, color: '#909399' },
  { id: 15, name: '重点跟进', count: 70, color: '#f56c6c' }
])

const maxTagCount = computed(() => {
  return Math.max(...tagStatistics.value.map(t => t.count))
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

    const res = await getCallStatisticsApi({ ...queryParams, type: 'customer' })
    const data = res.data

    Object.assign(statistics, data.overview || {})

    // 更新图表
    updateCharts()
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  } finally {
    loading.value = false
  }
}

// 更新图表
const updateCharts = () => {
  // 等级分布
  if (levelChart.value) {
    const chart = echarts.getInstanceByDom(levelChart.value) || echarts.init(levelChart.value)
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      series: [
        {
          name: '客户等级',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          label: {
            show: false,
            position: 'center'
          },
          labelLine: {
            show: false
          },
          data: [
            { value: statistics.level_breakdown[0].count, name: '普通客户', itemStyle: { color: '#909399' } },
            { value: statistics.level_breakdown[1].count, name: 'VIP客户', itemStyle: { color: '#e6a23c' } },
            { value: statistics.level_breakdown[2].count, name: '重要客户', itemStyle: { color: '#f56c6c' } }
          ]
        }
      ]
    }
    chart.setOption(option)
  }

  // 状态分布
  if (statusChart.value) {
    const chart = echarts.getInstanceByDom(statusChart.value) || echarts.init(statusChart.value)
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      series: [
        {
          name: '客户状态',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          label: {
            show: false,
            position: 'center'
          },
          labelLine: {
            show: false
          },
          data: [
            { value: statistics.status_breakdown[0].count, name: '待联系', itemStyle: { color: '#909399' } },
            { value: statistics.status_breakdown[1].count, name: '联系中', itemStyle: { color: '#409eff' } },
            { value: statistics.status_breakdown[2].count, name: '有意向', itemStyle: { color: '#67c23a' } },
            { value: statistics.status_breakdown[3].count, name: '已成交', itemStyle: { color: '#f56c6c' } },
            { value: statistics.status_breakdown[4].count, name: '已拒绝', itemStyle: { color: '#e6a23c' } },
            { value: statistics.status_breakdown[5].count, name: '无效客户', itemStyle: { color: '#f0f2f5' } }
          ]
        }
      ]
    }
    chart.setOption(option)
  }

  // 来源分布
  if (sourceChart.value) {
    const chart = echarts.getInstanceByDom(sourceChart.value) || echarts.init(sourceChart.value)
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      series: [
        {
          name: '客户来源',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          label: {
            show: false,
            position: 'center'
          },
          labelLine: {
            show: false
          },
          data: [
            { value: statistics.source_breakdown[0].count, name: '网站注册', itemStyle: { color: '#409eff' } },
            { value: statistics.source_breakdown[1].count, name: '线上推广', itemStyle: { color: '#67c23a' } },
            { value: statistics.source_breakdown[2].count, name: '朋友介绍', itemStyle: { color: '#e6a23c' } },
            { value: statistics.source_breakdown[3].count, name: '线下活动', itemStyle: { color: '#f56c6c' } },
            { value: statistics.source_breakdown[4].count, name: '其他', itemStyle: { color: '#909399' } }
          ]
        }
      ]
    }
    chart.setOption(option)
  }

  // 增长趋势
  if (growthChart.value) {
    const chart = echarts.getInstanceByDom(growthChart.value) || echarts.init(growthChart.value)
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
        data: ['新增客户', '总客户数', '转化客户']
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
        data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '新增客户',
          type: 'line',
          smooth: true,
          data: [120, 132, 101, 134, 90, 230, 210, 180, 220, 250, 280, 320],
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
          name: '总客户数',
          type: 'line',
          smooth: true,
          data: [500, 632, 733, 867, 957, 1187, 1397, 1577, 1797, 2047, 2327, 2647],
          itemStyle: {
            color: '#67c23a'
          }
        },
        {
          name: '转化客户',
          type: 'line',
          smooth: true,
          data: [30, 45, 35, 50, 28, 65, 70, 60, 80, 95, 100, 120],
          itemStyle: {
            color: '#e6a23c'
          }
        }
      ]
    }
    chart.setOption(option)
  }

  // 转化漏斗
  if (funnelChart.value) {
    const chart = echarts.getInstanceByDom(funnelChart.value) || echarts.init(funnelChart.value)
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      series: [
        {
          name: '转化漏斗',
          type: 'funnel',
          left: '10%',
          top: 60,
          bottom: 60,
          width: '80%',
          min: 0,
          max: 2000,
          minSize: '0%',
          maxSize: '100%',
          sort: 'descending',
          gap: 2,
          label: {
            show: true,
            position: 'inside',
            formatter: '{b}\n{c} ({d}%)'
          },
          labelLine: {
            show: false
          },
          itemStyle: {
            borderColor: '#fff',
            borderWidth: 2
          },
          emphasis: {
            label: {
              fontSize: 16
            }
          },
          data: [
            { value: 2000, name: '获取线索', itemStyle: { color: '#409eff' } },
            { value: 1500, name: '首次联系', itemStyle: { color: '#67c23a' } },
            { value: 1000, name: '需求沟通', itemStyle: { color: '#e6a23c' } },
            { value: 500, name: '方案报价', itemStyle: { color: '#f56c6c' } },
            { value: 250, name: '商务谈判', itemStyle: { color: '#909399' } },
            { value: 120, name: '成交客户', itemStyle: { color: '#f0f2f5' } }
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

onMounted(() => {
  getUserList()
  getStatistics()

  window.addEventListener('resize', () => {
    const charts = [levelChart, statusChart, sourceChart, growthChart, funnelChart]
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
.customer-analysis-report {
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

  .chart-legend {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    padding: 15px;
    border-top: 1px solid #f0f0f0;
    margin-top: 10px;

    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;

      .legend-color {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        flex-shrink: 0;
      }

      .legend-text {
        flex: 1;
      }

      .legend-count {
        color: #606266;
      }

      .legend-percent {
        color: #909399;
        margin-left: 5px;
      }
    }
  }

  .tag-cloud {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    padding: 20px;
    align-items: center;
    justify-content: center;
    min-height: 200px;

    .tag-item {
      padding: 6px 12px;
      border-radius: 20px;
      cursor: pointer;
      transition: all 0.3s;
      font-weight: 500;

      &:hover {
        transform: scale(1.1);
      }

      .tag-count {
        font-size: 0.8em;
        opacity: 0.8;
      }
    }
  }
}
</style>
