<template>
  <div class="call-task-container">
    <!-- 搜索区域 -->
    <div class="common-card">
      <el-form :model="queryParams" ref="queryFormRef" :inline="true" label-width="80px">
        <el-form-item label="任务名称" prop="keyword">
          <el-input
            v-model="queryParams.keyword"
            placeholder="请输入任务名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="任务状态" prop="status">
          <el-select
            v-model="queryParams.status"
            placeholder="请选择任务状态"
            clearable
            style="width: 150px"
          >
            <el-option label="全部" :value="null" />
            <el-option label="待执行" :value="1" />
            <el-option label="执行中" :value="2" />
            <el-option label="已暂停" :value="3" />
            <el-option label="已完成" :value="4" />
            <el-option label="已取消" :value="5" />
          </el-select>
        </el-form-item>
        <el-form-item label="创建时间">
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
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建任务
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 表格区域 -->
    <div class="common-card">
      <el-table
        v-loading="loading"
        :data="taskList"
        border
        stripe
      >
        <el-table-column prop="name" label="任务名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="total_count" label="号码总数" width="100" align="center" />
        <el-table-column prop="completed_count" label="已拨打" width="100" align="center" />
        <el-table-column prop="success_count" label="接通" width="100" align="center" />
        <el-table-column label="完成进度" width="150" align="center">
          <template #default="scope">
            <el-progress
              :percentage="Math.round((scope.row.completed_count / scope.row.total_count) * 100)"
              :stroke-width="10"
              :show-text="true"
            />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)" size="small">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="caller_number" label="主叫号码" width="130" />
        <el-table-column prop="start_time" label="开始时间" width="160" />
        <el-table-column prop="end_time" label="结束时间" width="160" />
        <el-table-column prop="create_user_name" label="创建人" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button
              type="success"
              text
              size="small"
              @click="handleStart(scope.row)"
              v-if="scope.row.status === 1 || scope.row.status === 3"
            >
              启动
            </el-button>
            <el-button
              type="warning"
              text
              size="small"
              @click="handlePause(scope.row)"
              v-if="scope.row.status === 2"
            >
              暂停
            </el-button>
            <el-button
              type="primary"
              text
              size="small"
              @click="viewDetail(scope.row)"
            >
              详情
            </el-button>
            <el-button
              type="danger"
              text
              size="small"
              @click="handleCancel(scope.row)"
              v-if="scope.row.status !== 4 && scope.row.status !== 5"
            >
              取消
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

    <!-- 新建/编辑任务对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      destroy-on-close
    >
      <el-form :model="taskForm" ref="taskFormRef" label-width="100px" :rules="rules">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="主叫号码" prop="caller_number_id">
          <el-select
            v-model="taskForm.caller_number_id"
            placeholder="请选择主叫号码"
            style="width: 100%"
          >
            <el-option
              v-for="number in callerNumberList"
              :key="number.id"
              :label="`${number.number} (${number.description || '默认'})`"
              :value="number.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="呼叫时段">
          <el-time-picker
            v-model="taskForm.time_range"
            is-range
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            style="width: 100%"
            format="HH:mm"
            value-format="HH:mm"
          />
          <div class="tip">仅在设置的时段内进行呼叫，默认 09:00-21:00</div>
        </el-form-item>
        <el-form-item label="呼叫间隔">
          <el-input-number
            v-model="taskForm.call_interval"
            :min="1"
            :max="60"
            placeholder="秒"
            style="width: 120px"
          />
          <span class="ml-2">秒，两次呼叫之间的间隔时间</span>
        </el-form-item>
        <el-form-item label="重试次数">
          <el-input-number
            v-model="taskForm.retry_count"
            :min="0"
            :max="5"
            style="width: 120px"
          />
          <span class="ml-2">次，未接通时的重试次数</span>
        </el-form-item>
        <el-form-item label="重试间隔">
          <el-input-number
            v-model="taskForm.retry_interval"
            :min="60"
            :max="3600"
            placeholder="秒"
            style="width: 120px"
          />
          <span class="ml-2">秒，重试的间隔时间</span>
        </el-form-item>
        <el-form-item label="号码列表">
          <el-upload
            class="upload-demo"
            :auto-upload="false"
            :show-file-list="true"
            accept=".csv,.xlsx,.xls"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
          >
            <template #trigger>
              <el-button type="primary">选择文件</el-button>
            </template>
            <el-button type="success" @click="downloadTemplate" style="margin-left: 10px">
              下载模板
            </el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持 csv/xlsx/xls 格式，文件需包含 name, phone 两列
              </div>
            </template>
          </el-upload>
          <div v-if="uploadedNumbers.length > 0" class="uploaded-numbers">
            <div class="uploaded-count">
              已上传 <strong>{{ uploadedNumbers.length }}</strong> 个号码
            </div>
            <el-table :data="uploadedNumbers.slice(0, 5)" border size="small">
              <el-table-column prop="name" label="姓名" />
              <el-table-column prop="phone" label="电话号码" />
            </el-table>
            <div v-if="uploadedNumbers.length > 5" class="more-numbers">
              ... 还有 {{ uploadedNumbers.length - 5 }} 个号码
            </div>
          </div>
        </el-form-item>
        <el-form-item label="任务描述">
          <el-input
            v-model="taskForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入任务描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTask" :loading="saveLoading">保存</el-button>
      </template>
    </el-dialog>

    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="任务详情"
      width="800px"
    >
      <div v-if="currentTask" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务名称">
            {{ currentTask.name }}
          </el-descriptions-item>
          <el-descriptions-item label="任务状态">
            <el-tag :type="getStatusTagType(currentTask.status)" size="small">
              {{ getStatusText(currentTask.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="主叫号码">
            {{ currentTask.caller_number }}
          </el-descriptions-item>
          <el-descriptions-item label="呼叫时段">
            {{ currentTask.start_time_range }} - {{ currentTask.end_time_range }}
          </el-descriptions-item>
          <el-descriptions-item label="呼叫间隔">
            {{ currentTask.call_interval }} 秒
          </el-descriptions-item>
          <el-descriptions-item label="重试次数">
            {{ currentTask.retry_count }} 次
          </el-descriptions-item>
          <el-descriptions-item label="号码总数">
            {{ currentTask.total_count }} 个
          </el-descriptions-item>
          <el-descriptions-item label="已拨打">
            {{ currentTask.completed_count }} 个
          </el-descriptions-item>
          <el-descriptions-item label="接通">
            {{ currentTask.success_count }} 个
          </el-descriptions-item>
          <el-descriptions-item label="接通率">
            {{ currentTask.total_count > 0 ? Math.round((currentTask.success_count / currentTask.total_count) * 100) : 0 }}%
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ currentTask.start_time || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ currentTask.end_time || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建人">
            {{ currentTask.create_user_name }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ currentTask.created_at }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 执行进度 -->
        <div class="progress-section mt-20">
          <h4>执行进度</h4>
          <el-progress
            :percentage="Math.round((currentTask.completed_count / currentTask.total_count) * 100)"
            :stroke-width="15"
            :show-text="true"
          />
          <div class="progress-stats mt-10">
            <el-row :gutter="20">
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-value" style="color: #409eff">{{ currentTask.total_count }}</div>
                  <div class="stat-label">总号码</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-value" style="color: #e6a23c">{{ currentTask.completed_count }}</div>
                  <div class="stat-label">已拨打</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-value" style="color: #67c23a">{{ currentTask.success_count }}</div>
                  <div class="stat-label">已接通</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="stat-item">
                  <div class="stat-value" style="color: #f56c6c">{{ currentTask.failed_count }}</div>
                  <div class="stat-label">未接通</div>
                </div>
              </el-col>
            </el-row>
          </div>
        </div>

        <!-- 任务描述 -->
        <div class="description-section mt-20" v-if="currentTask.description">
          <h4>任务描述</h4>
          <el-card>
            {{ currentTask.description }}
          </el-card>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="success" @click="exportTaskReport" v-if="currentTask.status === 4">
          导出报表
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Download } from '@element-plus/icons-vue'
import {
  getCallTaskListApi,
  createCallTaskApi,
  updateCallTaskApi,
  startCallTaskApi,
  pauseCallTaskApi,
  cancelCallTaskApi,
  getCallerNumberListApi
} from '@/api/call'

const loading = ref(false)
const queryFormRef = ref(null)
const taskFormRef = ref(null)
const taskList = ref([])
const callerNumberList = ref([])
const total = ref(0)
const dateRange = ref([])
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const currentTask = ref(null)
const saveLoading = ref(false)
const uploadedFile = ref(null)
const uploadedNumbers = ref([])

// 查询参数
const queryParams = reactive({
  page: 1,
  page_size: 20,
  keyword: '',
  status: null,
  start_time: '',
  end_time: ''
})

// 表单初始值
const initTaskForm = {
  name: '',
  caller_number_id: null,
  time_range: ['09:00', '21:00'],
  call_interval: 3,
  retry_count: 1,
  retry_interval: 300,
  description: ''
}

const taskForm = reactive({ ...initTaskForm })

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' },
    { min: 2, max: 50, message: '任务名称长度在 2 到 50 个字符之间', trigger: 'blur' }
  ],
  caller_number_id: [
    { required: true, message: '请选择主叫号码', trigger: 'change' }
  ]
}

const dialogTitle = computed(() => currentTask.value ? '编辑任务' : '新建任务')

// 获取任务列表
const getTaskList = async () => {
  loading.value = true
  try {
    if (dateRange.value && dateRange.value.length === 2) {
      queryParams.start_time = dateRange.value[0]
      queryParams.end_time = dateRange.value[1]
    } else {
      queryParams.start_time = ''
      queryParams.end_time = ''
    }

    const res = await getCallTaskListApi(queryParams)
    taskList.value = res.data.list.map(item => ({
      ...item,
      failed_count: item.completed_count - item.success_count
    }))
    total.value = res.data.total
  } catch (error) {
    ElMessage.error(error.message || '获取任务列表失败')
  } finally {
    loading.value = false
  }
}

// 获取主叫号码列表
const getCallerNumberList = async () => {
  try {
    const res = await getCallerNumberListApi()
    callerNumberList.value = res.data.list
  } catch (error) {
    ElMessage.error('获取主叫号码列表失败')
  }
}

// 搜索
const handleQuery = () => {
  queryParams.page = 1
  getTaskList()
}

// 重置
const resetQuery = () => {
  queryFormRef.value?.resetFields()
  dateRange.value = []
  handleQuery()
}

// 新建任务
const handleCreate = () => {
  currentTask.value = null
  Object.assign(taskForm, initTaskForm)
  uploadedFile.value = null
  uploadedNumbers.value = []
  dialogVisible.value = true
}

// 文件变化
const handleFileChange = (file) => {
  uploadedFile.value = file.raw

  // 模拟解析文件内容
  uploadedNumbers.value = [
    { name: '张三', phone: '13800138001' },
    { name: '李四', phone: '13800138002' },
    { name: '王五', phone: '13800138003' },
    { name: '赵六', phone: '13800138004' },
    { name: '钱七', phone: '13800138005' },
    { name: '孙八', phone: '13800138006' }
  ]
}

// 移除文件
const handleFileRemove = () => {
  uploadedFile.value = null
  uploadedNumbers.value = []
}

// 下载模板
const downloadTemplate = () => {
  ElMessage.info('模板下载功能开发中')
}

// 保存任务
const saveTask = async () => {
  if (!taskFormRef.value) return

  await taskFormRef.value.validate(async (valid) => {
    if (!valid) return

    if (!uploadedFile.value && !currentTask.value) {
      ElMessage.warning('请上传号码文件')
      return
    }

    saveLoading.value = true
    try {
      const formData = new FormData()
      Object.keys(taskForm).forEach(key => {
        if (key === 'time_range') {
          formData.append('start_time_range', taskForm.time_range[0])
          formData.append('end_time_range', taskForm.time_range[1])
        } else {
          formData.append(key, taskForm[key])
        }
      })

      if (uploadedFile.value) {
        formData.append('file', uploadedFile.value)
      }

      if (currentTask.value) {
        await updateCallTaskApi(currentTask.value.id, formData)
        ElMessage.success('任务更新成功')
      } else {
        await createCallTaskApi(formData)
        ElMessage.success('任务创建成功')
      }

      dialogVisible.value = false
      getTaskList()
    } catch (error) {
      ElMessage.error(error.message || '保存失败')
    } finally {
      saveLoading.value = false
    }
  })
}

// 启动任务
const handleStart = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要启动任务 "${row.name}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await startCallTaskApi(row.id)
    ElMessage.success('任务已启动')
    getTaskList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '启动失败')
    }
  }
}

// 暂停任务
const handlePause = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要暂停任务 "${row.name}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await pauseCallTaskApi(row.id)
    ElMessage.success('任务已暂停')
    getTaskList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '暂停失败')
    }
  }
}

// 取消任务
const handleCancel = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消任务 "${row.name}" 吗？取消后无法恢复。`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await cancelCallTaskApi(row.id)
    ElMessage.success('任务已取消')
    getTaskList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '取消失败')
    }
  }
}

// 查看详情
const viewDetail = (row) => {
  currentTask.value = {
    ...row,
    start_time_range: '09:00',
    end_time_range: '21:00',
    call_interval: 3,
    retry_count: 1,
    retry_interval: 300,
    failed_count: row.completed_count - row.success_count
  }
  detailDialogVisible.value = true
}

// 导出任务报表
const exportTaskReport = () => {
  ElMessage.info('导出功能开发中')
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const typeMap = {
    1: 'info',
    2: 'primary',
    3: 'warning',
    4: 'success',
    5: 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const textMap = {
    1: '待执行',
    2: '执行中',
    3: '已暂停',
    4: '已完成',
    5: '已取消'
  }
  return textMap[status] || '未知'
}

onMounted(() => {
  getTaskList()
  getCallerNumberList()
})
</script>

<style lang="scss" scoped>
.call-task-container {
  .tip {
    font-size: 12px;
    color: #909399;
    margin-top: 5px;
  }

  .uploaded-numbers {
    margin-top: 15px;

    .uploaded-count {
      margin-bottom: 10px;
      color: #67c23a;
    }

    .more-numbers {
      text-align: center;
      color: #909399;
      padding: 5px 0;
      font-size: 14px;
    }
  }

  .detail-content {
    .progress-section {
      h4 {
        margin-bottom: 10px;
        font-size: 16px;
        font-weight: bold;
      }

      .progress-stats {
        .stat-item {
          text-align: center;
          padding: 15px;
          background: #f5f7fa;
          border-radius: 8px;

          .stat-value {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
          }

          .stat-label {
            color: #909399;
            font-size: 14px;
          }
        }
      }
    }

    .description-section {
      h4 {
        margin-bottom: 10px;
        font-size: 16px;
        font-weight: bold;
      }
    }
  }
}
</style>
