<template>
  <div class="customer-detail-container">
    <div class="detail-header common-card">
      <div class="customer-basic">
        <el-avatar :size="80" class="customer-avatar">
          {{ customerInfo.name?.charAt(0) || '客' }}
        </el-avatar>
        <div class="customer-info">
          <div class="customer-name">
            {{ customerInfo.name }}
            <el-tag :type="getLevelTagType(customerInfo.level)" size="small" class="ml-2">
              {{ getLevelText(customerInfo.level) }}
            </el-tag>
            <el-tag :type="getStatusTagType(customerInfo.status)" size="small" class="ml-2">
              {{ getStatusText(customerInfo.status) }}
            </el-tag>
          </div>
          <div class="customer-contact">
            <span class="contact-item">
              <el-icon><Phone /></el-icon>
              {{ customerInfo.phone }}
              <el-button type="primary" link @click="handleCall">外呼</el-button>
            </span>
            <span class="contact-item" v-if="customerInfo.email">
              <el-icon><Message /></el-icon>
              {{ customerInfo.email }}
            </span>
            <span class="contact-item" v-if="customerInfo.company">
              <el-icon><OfficeBuilding /></el-icon>
              {{ customerInfo.company }}
            </span>
          </div>
          <div class="customer-tags">
            <el-tag
              v-for="tag in customerInfo.tags || []"
              :key="tag"
              size="small"
              style="margin-right: 5px"
            >
              {{ tag }}
            </el-tag>
          </div>
        </div>
        <div class="customer-actions">
          <el-button type="primary" @click="handleEdit">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button type="success" @click="handleAddFollow">
            <el-icon><ChatDotRound /></el-icon>
            跟进
          </el-button>
          <el-button @click="$router.back()">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
        </div>
      </div>
    </div>
    <el-tabs v-model="activeTab" class="detail-tabs">
      <el-tab-pane label="基本信息" name="basic">
        <div class="common-card">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="客户姓名">
              {{ customerInfo.name }}
            </el-descriptions-item>
            <el-descriptions-item label="手机号码">
              {{ customerInfo.phone }}
            </el-descriptions-item>
            <el-descriptions-item label="性别">
              {{ getGenderText(customerInfo.gender) }}
            </el-descriptions-item>
            <el-descriptions-item label="年龄">
              {{ customerInfo.age || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="电子邮箱">
              {{ customerInfo.email || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="公司名称">
              {{ customerInfo.company || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="职位">
              {{ customerInfo.position || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="客户来源">
              {{ customerInfo.source || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="联系地址">
              {{ customerInfo.address || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="所属坐席">
              {{ customerInfo.assign_user_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="分配时间">
              {{ customerInfo.assign_time || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="客户描述">
              {{ customerInfo.description || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="备注">
              {{ customerInfo.remark || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ customerInfo.created_at }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-tab-pane>
      <el-tab-pane label="跟进记录" name="follow">
        <div class="common-card">
          <follow-record :customer-id="customerId" />
        </div>
      </el-tab-pane>
      <el-tab-pane label="通话记录" name="call">
        <div class="common-card">
          <el-table :data="callRecordList" border stripe v-loading="callLoading">
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
                {{ formatDuration(scope.row.duration) }}
              </template>
            </el-table-column>
            <el-table-column prop="start_time" label="呼叫时间" width="160" />
            <el-table-column prop="recording_url" label="录音" width="100" align="center">
              <template #default="scope">
                <el-button
                  type="primary"
                  link
                  size="small"
                  v-if="scope.row.recording_url"
                  @click="playRecording(scope.row)"
                >
                  播放
                </el-button>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="scope">
                <el-button
                  type="primary"
                  text
                  size="small"
                  @click="viewCallDetail(scope.row)"
                >
                  详情
                </el-button>
                <el-button
                  type="success"
                  text
                  size="small"
                  @click="downloadRecording(scope.row)"
                  v-if="scope.row.recording_url"
                >
                  下载
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <!-- 分页 -->
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="callQuery.page"
              v-model:page-size="callQuery.page_size"
              :total="callTotal"
              :page-sizes="[10, 20, 30, 50]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="getCallRecordList"
              @current-change="getCallRecordList"
            />
          </div>
        </div>
      </el-tab-pane>
      <el-tab-pane label="统计信息" name="stat">
        <div class="common-card">
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="stat-card">
                <p class="stat-title">跟进次数</p>
                <h3 class="stat-value">{{ customerInfo.follow_count || 0 }}</h3>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <p class="stat-title">通话次数</p>
                <h3 class="stat-value">{{ customerInfo.call_count || 0 }}</h3>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <p class="stat-title">总通话时长</p>
                <h3 class="stat-value">{{ formatDuration(customerInfo.total_call_duration || 0) }}</h3>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <p class="stat-title">上次跟进时间</p>
                <h3 class="stat-value">{{ customerInfo.last_follow_time || '-' }}</h3>
              </div>
            </el-col>
          </el-row>
          <div class="mt-20">
            <h4>跟进趋势</h4>
            <div ref="trendChartRef" style="height: 300px; margin-top: 20px"></div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="编辑客户"
      width="700px"
      destroy-on-close
    >
      <customer-form
        ref="customerFormRef"
        :customer-id="customerId"
        @success="getCustomerDetail"
      />
    </el-dialog>
    <!-- 跟进记录对话框 -->
    <el-dialog
      v-model="followDialogVisible"
      title="添加跟进记录"
      width="700px"
    >
      <follow-record :customer-id="customerId" />
    </el-dialog>

    <!-- 录音播放对话框 -->
    <el-dialog
      v-model="audioVisible"
      title="录音播放"
      width="500px"
    >
      <div v-if="currentAudio.url" class="audio-player">
        <p class="audio-name">{{ currentAudio.name }}</p>
        <p class="audio-duration">时长：{{ formatDuration(currentAudio.duration) }}</p>
        <audio :src="currentAudio.url" controls style="width: 100%; margin: 20px 0;" />
        <div class="audio-actions">
          <el-button type="primary" @click="downloadRecording(currentAudio)">
            <el-icon><Download /></el-icon>
            下载录音
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 通话详情对话框 -->
    <el-dialog
      v-model="callDetailVisible"
      title="通话详情"
      width="600px"
    >
      <div v-if="currentCall" class="call-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="主叫号码">
            {{ currentCall.caller }}
          </el-descriptions-item>
          <el-descriptions-item label="被叫号码">
            {{ currentCall.called }}
          </el-descriptions-item>
          <el-descriptions-item label="呼叫方向">
            <el-tag :type="currentCall.direction === 1 ? 'primary' : 'success'" size="small">
              {{ currentCall.direction === 1 ? '外呼' : '呼入' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="通话状态">
            <el-tag :type="getStatusTagType(currentCall.status)" size="small">
              {{ getStatusText(currentCall.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="通话时长">
            {{ formatDuration(currentCall.duration) }}
          </el-descriptions-item>
          <el-descriptions-item label="呼叫时间">
            {{ currentCall.start_time }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ currentCall.end_time || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="坐席">
            {{ currentCall.agent_name || '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="currentCall.recording_url" class="call-recording mt-20">
          <h4>通话录音</h4>
          <audio :src="currentCall.recording_url" controls style="width: 100%; margin: 10px 0;" />
          <el-button type="primary" size="small" @click="downloadRecording(currentCall)">
            <el-icon><Download /></el-icon>
            下载录音
          </el-button>
        </div>

        <div v-if="currentCall.remark" class="call-remark mt-20">
          <h4>通话备注</h4>
          <p>{{ currentCall.remark }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import CustomerForm from './components/CustomerForm.vue'
import FollowRecord from './components/FollowRecord.vue'
import { getCustomerDetailApi } from '@/api/customer'
import { formatDuration } from '@/utils/datetime'
const route = useRoute()
const customerId = ref(route.params.id)
const activeTab = ref('basic')
const dialogVisible = ref(false)
const followDialogVisible = ref(false)
const customerInfo = ref({})
const callLoading = ref(false)
const callRecordList = ref([])
const callTotal = ref(0)
const trendChartRef = ref(null)
// 录音播放相关
const audioVisible = ref(false)
const currentAudio = ref({
  url: '',
  name: '',
  duration: 0
})
// 通话详情相关
const callDetailVisible = ref(false)
const currentCall = ref(null)
// 通话记录查询参数
const callQuery = reactive({
  page: 1,
  page_size: 10,
  customer_id: customerId.value
})
// 获取客户详情
const getCustomerDetail = async () => {
  try {
    const res = await getCustomerDetailApi(customerId.value)
    customerInfo.value = res.data
    // 初始化图表
    initTrendChart()
  } catch (error) {
    ElMessage.error(error.message || '获取客户详情失败')
  }
}
// 获取通话记录
const getCallRecordList = async () => {
  // TODO: 实现获取通话记录接口
  callLoading.value = true
  try {
    // 模拟数据
    callRecordList.value = [
      {
        id: 1,
        caller: '13800138000',
        called: customerInfo.value.phone,
        direction: 1,
        status: 2,
        duration: 185,
        start_time: '2024-05-13 14:30:25',
        end_time: '2024-05-13 14:33:30',
        agent_name: '坐席1',
        recording_url: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3', // 示例音频
        remark: '客户对产品很感兴趣，约定下周二再次沟通'
      },
      {
        id: 2,
        caller: '13800138000',
        called: customerInfo.value.phone,
        direction: 1,
        status: 5,
        duration: 0,
        start_time: '2024-05-12 10:15:00',
        end_time: '2024-05-12 10:15:10',
        agent_name: '坐席1',
        recording_url: '',
        remark: '客户挂断电话'
      }
    ]
    callTotal.value = 2
  } catch (error) {
    ElMessage.error('获取通话记录失败')
  } finally {
    callLoading.value = false
  }
}
// 初始化趋势图表
const initTrendChart = () => {
  if (!trendChartRef.value) return
  const chart = echarts.init(trendChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '跟进次数',
        type: 'line',
        data: [2, 3, 1, 4, 2, 3],
        smooth: true,
        itemStyle: {
          color: '#409eff'
        }
      },
      {
        name: '通话时长',
        type: 'bar',
        data: [300, 500, 200, 600, 400, 550],
        itemStyle: {
          color: '#67c23a'
        }
      }
    ]
  }
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}
// 外呼客户
const handleCall = () => {
  // 跳转到呼叫中心页面，并自动填充客户号码
  ElMessage.success('跳转到外呼页面')
  // 可以通过路由传参，或者存到store里
  // $router.push({ name: 'Call', query: { phone: customerInfo.value.phone, customerId: customerId.value } })
}
// 编辑客户
const handleEdit = () => {
  dialogVisible.value = true
}
// 添加跟进
const handleAddFollow = () => {
  followDialogVisible.value = true
}
// 播放录音
const playRecording = (row) => {
  if (!row.recording_url) {
    ElMessage.warning('该通话没有录音文件')
    return
  }
  currentAudio.value = {
    url: row.recording_url,
    name: `${row.caller} 呼叫 ${row.called} 的录音`,
    duration: row.duration
  }
  audioVisible.value = true
}
// 下载录音
const downloadRecording = (row) => {
  if (!row.recording_url) {
    ElMessage.warning('该通话没有录音文件')
    return
  }
  // 创建a标签下载
  const a = document.createElement('a')
  a.href = row.recording_url
  a.download = `通话录音_${row.caller}_${row.called}_${row.start_time}.mp3`
  a.click()
  ElMessage.success('开始下载录音')
}
// 查看通话详情
const viewCallDetail = (row) => {
  currentCall.value = row
  callDetailVisible.value = true
}
// 获取等级标签类型
const getLevelTagType = (level) => {
  const typeMap = {
    1: 'info',
    2: 'warning',
    3: 'danger'
  }
  return typeMap[level] || 'info'
}
// 获取等级文本
const getLevelText = (level) => {
  const textMap = {
    1: '普通',
    2: 'VIP',
    3: '重要客户'
  }
  return textMap[level] || '未知'
}
// 获取状态标签类型
const getStatusTagType = (status) => {
  const typeMap = {
    1: 'info',
    2: 'primary',
    3: 'success',
    4: 'danger',
    5: 'warning',
    6: 'default'
  }
  return typeMap[status] || 'info'
}
// 获取状态文本
const getStatusText = (status) => {
  const textMap = {
    1: '待联系',
    2: '联系中',
    3: '有意向',
    4: '已成交',
    5: '已拒绝',
    6: '无效客户'
  }
  return textMap[status] || '未知'
}
// 获取性别文本
const getGenderText = (gender) => {
  const textMap = {
    0: '未知',
    1: '男',
    2: '女'
  }
  return textMap[gender] || '未知'
}
onMounted(() => {
  getCustomerDetail()
  getCallRecordList()
})
</script>
<style lang="scss" scoped>
.customer-detail-container {
  .detail-header {
    .customer-basic {
      display: flex;
      align-items: center;
      .customer-avatar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
        font-size: 32px;
        font-weight: bold;
        margin-right: 20px;
      }
      .customer-info {
        flex: 1;
        .customer-name {
          font-size: 24px;
          font-weight: bold;
          color: #303133;
          margin-bottom: 10px;
        }
        .customer-contact {
          margin-bottom: 10px;
          .contact-item {
            display: inline-flex;
            align-items: center;
            color: #606266;
            margin-right: 30px;
            .el-icon {
              margin-right: 5px;
              color: #909399;
            }
          }
        }
      }
      .customer-actions {
        display: flex;
        gap: 10px;
      }
    }
  }
  .detail-tabs {
    margin-top: 20px;
    :deep(.el-tabs__content) {
      padding: 0;
    }
  }
  .stat-card {
    padding: 20px;
    background: #f5f7fa;
    border-radius: 8px;
    text-align: center;
    .stat-title {
      color: #909399;
      font-size: 14px;
      margin-bottom: 10px;
    }
    .stat-value {
      font-size: 28px;
      font-weight: bold;
      color: #303133;
    }
  }
  // 录音播放器样式
  .audio-player {
    text-align: center;
    .audio-name {
      font-size: 16px;
      font-weight: bold;
      margin-bottom: 10px;
    }
    .audio-duration {
      color: #909399;
      margin-bottom: 20px;
    }
    .audio-actions {
      margin-top: 20px;
    }
  }
  // 通话详情样式
  .call-detail {
    h4 {
      font-size: 14px;
      font-weight: bold;
      margin-bottom: 10px;
    }
    .call-recording, .call-remark {
      padding: 15px;
      background: #f5f7fa;
      border-radius: 4px;
      p {
        margin: 0;
        color: #606266;
      }
    }
  }
}
</style>
