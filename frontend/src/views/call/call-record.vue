<template>
  <div class="call-record-container">
    <!-- 搜索区域 -->
    <div class="common-card">
      <el-form :model="queryParams" ref="queryFormRef" :inline="true" label-width="80px">
        <el-form-item label="电话号码" prop="keyword">
          <el-input
            v-model="queryParams.keyword"
            placeholder="请输入主叫/被叫号码"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="呼叫方向" prop="direction">
          <el-select
            v-model="queryParams.direction"
            placeholder="请选择呼叫方向"
            clearable
            style="width: 150px"
          >
            <el-option label="全部" :value="null" />
            <el-option label="外呼" :value="1" />
            <el-option label="呼入" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="通话状态" prop="status">
          <el-select
            v-model="queryParams.status"
            placeholder="请选择通话状态"
            clearable
            style="width: 150px"
          >
            <el-option label="全部" :value="null" />
            <el-option label="未接通" :value="1" />
            <el-option label="已接通" :value="2" />
            <el-option label="已拒绝" :value="3" />
            <el-option label="忙线" :value="4" />
            <el-option label="取消" :value="5" />
          </el-select>
        </el-form-item>
        <el-form-item label="坐席" prop="user_id">
          <el-select
            v-model="queryParams.user_id"
            placeholder="请选择坐席"
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
        <el-form-item label="呼叫时间">
          <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 380px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetQuery">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 操作按钮 -->
    <div class="common-card">
      <el-row :gutter="10">
        <el-col :span="24">
          <el-button type="success" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出记录
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 表格区域 -->
    <div class="common-card">
      <el-table
        v-loading="loading"
        :data="recordList"
        border
        stripe
      >
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
        <el-table-column prop="end_time" label="结束时间" width="160" />
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
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              text
              size="small"
              @click="viewDetail(scope.row)"
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
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.page_size"
          :total="total"
          :page-sizes="[10, 20, 30, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleQuery"
          @current-change="handleQuery"
        />
      </div>
    </div>

    <!-- 通话详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="通话详情"
      width="700px"
    >
      <div v-if="currentRecord" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="主叫号码">
            {{ currentRecord.caller }}
          </el-descriptions-item>
          <el-descriptions-item label="被叫号码">
            {{ currentRecord.called }}
          </el-descriptions-item>
          <el-descriptions-item label="呼叫方向">
            <el-tag :type="currentRecord.direction === 1 ? 'primary' : 'success'" size="small">
              {{ currentRecord.direction === 1 ? '外呼' : '呼入' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="通话状态">
            <el-tag :type="getStatusTagType(currentRecord.status)" size="small">
              {{ getStatusText(currentRecord.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="通话时长">
            {{ currentRecord.duration ? formatDuration(currentRecord.duration) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="坐席">
            {{ currentRecord.user_name }}
          </el-descriptions-item>
          <el-descriptions-item label="客户名称">
            {{ currentRecord.customer_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="呼叫时间">
            {{ currentRecord.start_time }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ currentRecord.end_time }}
          </el-descriptions-item>
          <el-descriptions-item label="挂断方">
            {{ currentRecord.hangup_side === 1 ? '坐席' : currentRecord.hangup_side === 2 ? '客户' : '系统' }}
          </el-descriptions-item>
          <el-descriptions-item label="通话录音" v-if="currentRecord.recording_url">
            <audio :src="currentRecord.recording_url" controls />
          </el-descriptions-item>
        </el-descriptions>

        <!-- 跟进记录 -->
        <div class="follow-section mt-20" v-if="currentRecord.follow_record">
          <h4>跟进记录</h4>
          <el-card>
            <div class="follow-info">
              <span class="follow-type">{{ getFollowTypeText(currentRecord.follow_record.type) }}</span>
              <span class="follow-time">{{ currentRecord.follow_record.follow_time }}</span>
            </div>
            <div class="follow-content mt-10">
              <p><strong>跟进内容：</strong>{{ currentRecord.follow_record.content }}</p>
              <p v-if="currentRecord.follow_record.result"><strong>跟进结果：</strong>{{ currentRecord.follow_record.result }}</p>
              <p v-if="currentRecord.follow_record.next_follow_time">
                <strong>下次跟进时间：</strong>{{ currentRecord.follow_record.next_follow_time }}
              </p>
            </div>
          </el-card>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button type="primary" @click="goToCustomerDetail" v-if="currentRecord?.customer_id">
          查看客户详情
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Download } from '@element-plus/icons-vue'
import { getCallRecordListApi, exportCallRecordApi } from '@/api/call'
import { getUserListApi } from '@/api/user'
import { formatDuration } from '@/utils/datetime'

const router = useRouter()
const loading = ref(false)
const queryFormRef = ref(null)
const recordList = ref([])
const userList = ref([])
const total = ref(0)
const dateRange = ref([])
const showDetailDialog = ref(false)
const currentRecord = ref(null)

// 查询参数
const queryParams = reactive({
  page: 1,
  page_size: 20,
  keyword: '',
  direction: null,
  status: null,
  user_id: null,
  start_time: '',
  end_time: ''
})

// 获取通话记录列表
const getCallRecordList = async () => {
  loading.value = true
  try {
    if (dateRange.value && dateRange.value.length === 2) {
      queryParams.start_time = dateRange.value[0]
      queryParams.end_time = dateRange.value[1]
    } else {
      queryParams.start_time = ''
      queryParams.end_time = ''
    }

    const res = await getCallRecordListApi(queryParams)
    recordList.value = res.data.list
    total.value = res.data.total
  } catch (error) {
    ElMessage.error(error.message || '获取通话记录失败')
  } finally {
    loading.value = false
  }
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

// 搜索
const handleQuery = () => {
  queryParams.page = 1
  getCallRecordList()
}

// 重置
const resetQuery = () => {
  queryFormRef.value?.resetFields()
  dateRange.value = []
  handleQuery()
}

// 导出记录
const handleExport = () => {
  ElMessage.info('导出功能开发中')
}

// 播放录音
const playRecording = (row) => {
  // 可以弹出一个播放器对话框，或者直接在新窗口打开
  window.open(row.recording_url, '_blank')
}

// 下载录音
const downloadRecording = (row) => {
  const a = document.createElement('a')
  a.href = row.recording_url
  a.download = `通话录音_${row.caller}_${row.called}_${row.start_time}.wav`
  a.click()
}

// 查看详情
const viewDetail = (row) => {
  currentRecord.value = {
    ...row,
    // 模拟跟进记录数据
    follow_record: row.status === 2 ? {
      type: 1,
      content: '客户表示对产品感兴趣，需要进一步了解价格详情',
      result: '已发送产品报价单',
      follow_time: row.start_time,
      next_follow_time: '2024-05-15 10:00:00'
    } : null
  }
  showDetailDialog.value = true
}

// 跳转到客户详情页
const goToCustomerDetail = () => {
  if (currentRecord.value?.customer_id) {
    router.push(`/customer/${currentRecord.value.customer_id}`)
    showDetailDialog.value = false
  }
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

// 获取跟进类型文本
const getFollowTypeText = (type) => {
  const textMap = {
    1: '电话跟进',
    2: '微信跟进',
    3: '线下拜访',
    4: '短信跟进',
    5: '邮件跟进'
  }
  return textMap[type] || '其他跟进'
}

onMounted(() => {
  getCallRecordList()
  getUserList()
})
</script>

<style lang="scss" scoped>
.call-record-container {
  .detail-content {
    audio {
      width: 100%;
    }

    .follow-section {
      h4 {
        margin-bottom: 10px;
        font-size: 16px;
        font-weight: bold;
      }

      .follow-info {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .follow-type {
          font-weight: bold;
          color: #409eff;
        }

        .follow-time {
          color: #909399;
          font-size: 14px;
        }
      }

      .follow-content {
        p {
          margin-bottom: 5px;
          color: #606266;
        }
      }
    }
  }
}
</style>
