<template>
  <div class="follow-record-container">
    <!-- 新增跟进记录 -->
    <div class="add-follow-section">
      <el-form :model="followForm" label-width="80px">
        <el-form-item label="跟进类型">
          <el-select v-model="followForm.type" style="width: 200px">
            <el-option label="电话跟进" :value="1" />
            <el-option label="微信跟进" :value="2" />
            <el-option label="线下拜访" :value="3" />
            <el-option label="短信跟进" :value="4" />
            <el-option label="邮件跟进" :value="5" />
          </el-select>
        </el-form-item>
        <el-form-item label="跟进内容">
          <el-input
            v-model="followForm.content"
            type="textarea"
            :rows="3"
            placeholder="请输入跟进内容"
          />
        </el-form-item>
        <el-form-item label="跟进结果">
          <el-input
            v-model="followForm.result"
            type="textarea"
            :rows="2"
            placeholder="请输入跟进结果"
          />
        </el-form-item>
        <el-form-item label="下次跟进">
          <el-date-picker
            v-model="followForm.next_follow_time"
            type="datetime"
            placeholder="请选择下次跟进时间"
            style="width: 240px"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="通话时长">
          <el-input-number
            v-model="followForm.duration"
            :min="0"
            placeholder="秒"
            style="width: 120px"
          />
          <span class="ml-2">秒</span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleAddFollow" :loading="addLoading">
            <el-icon><Plus /></el-icon>
            添加跟进记录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    <!-- 跟进记录列表 -->
    <div class="follow-list-section">
      <h3>历史跟进记录</h3>
      <div class="follow-timeline">
        <el-timeline v-loading="loading">
          <el-timeline-item
            v-for="item in followList"
            :key="item.id"
            :timestamp="item.follow_time"
            placement="top"
          >
            <template #dot>
              <el-icon :color="getTypeColor(item.type)" size="18">
                <component :is="getTypeIcon(item.type)" />
              </el-icon>
            </template>
            <el-card shadow="hover">
              <div class="follow-header">
                <div class="follow-info">
                  <span class="follow-type">{{ getTypeText(item.type) }}</span>
                  <span class="follow-user">跟进人：{{ item.user_name }}</span>
                  <span class="follow-duration" v-if="item.duration">
                    通话时长：{{ formatDuration(item.duration) }}
                  </span>
                </div>
                <div class="follow-actions">
                  <el-button
                    type="danger"
                    text
                    size="small"
                    @click="handleDelete(item)"
                  >
                    删除
                  </el-button>
                </div>
              </div>
              <div class="follow-content">
                <p><strong>跟进内容：</strong>{{ item.content }}</p>
                <p v-if="item.result"><strong>跟进结果：</strong>{{ item.result }}</p>
                <p v-if="item.next_follow_time">
                  <strong>下次跟进时间：</strong>{{ item.next_follow_time }}
                </p>
              </div>
            </el-card>
          </el-timeline-item>
          <div v-if="followList.length === 0 && !loading" class="empty-tip">
            暂无跟进记录
          </div>
        </el-timeline>
      </div>
      <!-- 分页 -->
      <div class="pagination-container" v-if="total > pageSize">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.page_size"
          :total="total"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="getFollowList"
          @current-change="getFollowList"
        />
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getFollowRecordListApi,
  createFollowRecordApi,
  deleteFollowRecordApi
} from '@/api/customer'
import { formatDuration } from '@/utils/datetime'
const props = defineProps({
  customerId: {
    type: Number,
    required: true
  }
})
const loading = ref(false)
const addLoading = ref(false)
const followList = ref([])
const total = ref(0)
const pageSize = ref(10)
// 查询参数
const queryParams = reactive({
  page: 1,
  page_size: 10,
  customer_id: props.customerId
})
// 跟进表单
const followForm = reactive({
  customer_id: props.customerId,
  type: 1,
  content: '',
  result: '',
  next_follow_time: '',
  duration: 0
})
// 获取跟进记录列表
const getFollowList = async () => {
  loading.value = true
  try {
    const res = await getFollowRecordListApi(queryParams)
    followList.value = res.data.list
    total.value = res.data.total
  } catch (error) {
    ElMessage.error(error.message || '获取跟进记录失败')
  } finally {
    loading.value = false
  }
}
// 添加跟进记录
const handleAddFollow = async () => {
  if (!followForm.content.trim()) {
    ElMessage.warning('请输入跟进内容')
    return
  }
  addLoading.value = true
  try {
    await createFollowRecordApi(followForm)
    ElMessage.success('添加成功')
    // 重置表单
    followForm.content = ''
    followForm.result = ''
    followForm.next_follow_time = ''
    followForm.duration = 0
    // 刷新列表
    getFollowList()
  } catch (error) {
    ElMessage.error(error.message || '添加失败')
  } finally {
    addLoading.value = false
  }
}
// 删除跟进记录
const handleDelete = (item) => {
  ElMessageBox.confirm(
    '确定要删除这条跟进记录吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteFollowRecordApi(item.id)
      ElMessage.success('删除成功')
      getFollowList()
    } catch (error) {
      ElMessage.error(error.message || '删除失败')
    }
  })
}
// 获取跟进类型图标
const getTypeIcon = (type) => {
  const iconMap = {
    1: 'Phone',
    2: 'ChatDotRound',
    3: 'Location',
    4: 'Message',
    5: 'Message'
  }
  return iconMap[type] || 'Document'
}
// 获取跟进类型颜色
const getTypeColor = (type) => {
  const colorMap = {
    1: '#409eff',
    2: '#67c23a',
    3: '#e6a23c',
    4: '#f56c6c',
    5: '#909399'
  }
  return colorMap[type] || '#909399'
}
// 获取跟进类型文本
const getTypeText = (type) => {
  const textMap = {
    1: '电话跟进',
    2: '微信跟进',
    3: '线下拜访',
    4: '短信跟进',
    5: '邮件跟进'
  }
  return textMap[type] || '其他跟进'
}
watch(() => props.customerId, (newVal) => {
  if (newVal) {
    queryParams.customer_id = newVal
    followForm.customer_id = newVal
    getFollowList()
  }
})
onMounted(() => {
  getFollowList()
})
</script>
<style lang="scss" scoped>
.follow-record-container {
  .add-follow-section {
    padding: 20px;
    background: #f5f7fa;
    border-radius: 8px;
    margin-bottom: 20px;
  }
  .follow-list-section {
    h3 {
      font-size: 16px;
      font-weight: bold;
      margin-bottom: 20px;
      color: #303133;
    }
    .follow-timeline {
      padding-left: 10px;
    }
    .follow-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
      .follow-info {
        .follow-type {
          font-weight: bold;
          color: #409eff;
          margin-right: 20px;
        }
        .follow-user,
        .follow-duration {
          color: #909399;
          font-size: 12px;
          margin-right: 20px;
        }
      }
    }
    .follow-content {
      p {
        line-height: 1.6;
        margin-bottom: 8px;
        color: #606266;
        &:last-child {
          margin-bottom: 0;
        }
      }
    }
    .empty-tip {
      text-align: center;
      color: #909399;
      padding: 40px 0;
    }
  }
}
</style>
