<template>
  <div class="logs-manage-container">
    <!-- 搜索区域 -->
    <div class="common-card">
      <el-form :model="queryParams" ref="queryFormRef" :inline="true" label-width="80px">
        <el-form-item label="操作人" prop="user_id">
          <el-select
            v-model="queryParams.user_id"
            placeholder="全部用户"
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
        <el-form-item label="操作类型" prop="operation_type">
          <el-select
            v-model="queryParams.operation_type"
            placeholder="全部类型"
            clearable
            style="width: 150px"
          >
            <el-option label="登录" value="login" />
            <el-option label="登出" value="logout" />
            <el-option label="新增" value="create" />
            <el-option label="编辑" value="update" />
            <el-option label="删除" value="delete" />
            <el-option label="查询" value="query" />
            <el-option label="导入" value="import" />
            <el-option label="导出" value="export" />
            <el-option label="上传" value="upload" />
            <el-option label="下载" value="download" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作模块" prop="module">
          <el-select
            v-model="queryParams.module"
            placeholder="全部模块"
            clearable
            style="width: 150px"
          >
            <el-option label="系统管理" value="system" />
            <el-option label="用户管理" value="user" />
            <el-option label="角色管理" value="role" />
            <el-option label="权限管理" value="permission" />
            <el-option label="客户管理" value="customer" />
            <el-option label="呼叫中心" value="call" />
            <el-option label="统计报表" value="report" />
            <el-option label="配置管理" value="config" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作状态" prop="status">
          <el-select
            v-model="queryParams.status"
            placeholder="全部状态"
            clearable
            style="width: 120px"
          >
            <el-option label="成功" :value="1" />
            <el-option label="失败" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作时间">
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
        <el-form-item label="关键词" prop="keyword">
          <el-input
            v-model="queryParams.keyword"
            placeholder="操作内容/IP"
            clearable
            style="width: 200px"
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
          <el-button type="success" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出日志
          </el-button>
          <el-button type="danger" @click="handleClear" :disabled="!allowClear">
            <el-icon><Delete /></el-icon>
            清空日志
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 统计信息 -->
    <div class="common-card mt-4">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ statistics.total_count }}</div>
            <div class="stat-label">总操作次数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item success">
            <div class="stat-value">{{ statistics.success_count }}</div>
            <div class="stat-label">成功次数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item danger">
            <div class="stat-value">{{ statistics.fail_count }}</div>
            <div class="stat-label">失败次数</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item warning">
            <div class="stat-value">{{ statistics.today_count }}</div>
            <div class="stat-label">今日操作次数</div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 日志表格 -->
    <div class="common-card mt-4">
      <el-table
        v-loading="loading"
        :data="logList"
        border
        stripe
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="user_name" label="操作人" width="120" />
        <el-table-column prop="user_ip" label="IP地址" width="130" />
        <el-table-column prop="user_agent" label="User Agent" min-width="200" show-overflow-tooltip>
          <template #default="scope">
            <el-tooltip placement="top" :content="scope.row.user_agent" show-after="500">
              <span>{{ scope.row.user_agent }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="模块" width="100" align="center">
          <template #default="scope">
            <el-tag size="small" :type="getModuleTagType(scope.row.module)">
              {{ getModuleName(scope.row.module) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operation_type" label="操作类型" width="100" align="center">
          <template #default="scope">
            <el-tag size="small" :type="getOperationTypeTagType(scope.row.operation_type)">
              {{ getOperationTypeName(scope.row.operation_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operation_desc" label="操作描述" min-width="250" show-overflow-tooltip />
        <el-table-column prop="request_url" label="请求路径" min-width="200" show-overflow-tooltip />
        <el-table-column prop="request_method" label="请求方法" width="100" align="center">
          <template #default="scope">
            <el-tag size="small" :type="getMethodTagType(scope.row.request_method)">
              {{ scope.row.request_method }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'" size="small">
              {{ scope.row.status === 1 ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时" width="100" align="center">
          <template #default="scope">
            <span :class="scope.row.duration > 1000 ? 'text-red-500' : 'text-gray-600'">
              {{ scope.row.duration }}ms
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="error_msg" label="错误信息" min-width="150" show-overflow-tooltip v-if="showErrorColumn">
          <template #default="scope">
            <span class="text-red-500" v-if="scope.row.status === 2">{{ scope.row.error_msg || '-' }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="操作时间" width="160" align="center" sortable />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              text
              size="small"
              @click="viewDetail(scope.row)"
            >
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
          :page-sizes="[10, 20, 50, 100, 200]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleQuery"
          @current-change="handleQuery"
        />
      </div>
    </div>

    <!-- 日志详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="操作日志详情"
      width="800px"
    >
      <div v-if="currentLog" class="log-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="操作人">{{ currentLog.user_name }}</el-descriptions-item>
          <el-descriptions-item label="操作时间">{{ currentLog.created_at }}</el-descriptions-item>
          <el-descriptions-item label="IP地址">{{ currentLog.user_ip }}</el-descriptions-item>
          <el-descriptions-item label="操作状态">
            <el-tag :type="currentLog.status === 1 ? 'success' : 'danger'" size="small">
              {{ currentLog.status === 1 ? '成功' : '失败' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="操作模块">{{ getModuleName(currentLog.module) }}</el-descriptions-item>
          <el-descriptions-item label="操作类型">{{ getOperationTypeName(currentLog.operation_type) }}</el-descriptions-item>
          <el-descriptions-item label="请求方法">{{ currentLog.request_method }}</el-descriptions-item>
          <el-descriptions-item label="请求耗时">{{ currentLog.duration }}ms</el-descriptions-item>
          <el-descriptions-item label="请求路径" :span="2">{{ currentLog.request_url }}</el-descriptions-item>
          <el-descriptions-item label="操作描述" :span="2">{{ currentLog.operation_desc }}</el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">请求参数</el-divider>
        <pre class="code-block">{{ formatJson(currentLog.request_params) }}</pre>

        <el-divider content-position="left">响应结果</el-divider>
        <pre class="code-block" :class="currentLog.status === 2 ? 'error' : ''">
          {{ formatJson(currentLog.response_data) }}
        </pre>

        <el-divider content-position="left">浏览器信息</el-divider>
        <p>{{ currentLog.user_agent }}</p>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 清空日志确认对话框 -->
    <el-dialog
      v-model="clearDialogVisible"
      title="清空操作日志"
      width="500px"
    >
      <el-alert
        title="警告"
        type="warning"
        description="此操作将清空所有操作日志，删除后无法恢复，请谨慎操作！"
        show-icon
        style="margin-bottom: 20px"
      />
      <el-form label-width="100px">
        <el-form-item label="请确认">
          <el-checkbox v-model="clearConfirm">我已了解此操作的风险，确认要清空所有操作日志</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="clearDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmClear" :loading="clearLoading" :disabled="!clearConfirm">确认清空</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Download, Delete } from '@element-plus/icons-vue'

const loading = ref(false)
const queryFormRef = ref(null)
const userList = ref([])
const logList = ref([])
const total = ref(0)
const dateRange = ref([])
const detailDialogVisible = ref(false)
const clearDialogVisible = ref(false)
const currentLog = ref(null)
const clearLoading = ref(false)
const clearConfirm = ref(false)
const allowClear = ref(true) // 超级管理员才显示清空按钮
const showErrorColumn = ref(true)

// 统计数据
const statistics = reactive({
  total_count: 0,
  success_count: 0,
  fail_count: 0,
  today_count: 0
})

// 查询参数
const queryParams = reactive({
  page: 1,
  page_size: 20,
  user_id: null,
  operation_type: null,
  module: null,
  status: null,
  keyword: '',
  start_time: '',
  end_time: ''
})

// 获取用户列表
const getUserList = async () => {
  try {
    // 模拟数据
    userList.value = [
      { id: 1, username: 'admin', nickname: '超级管理员' },
      { id: 2, username: 'manager', nickname: '部门经理' },
      { id: 3, username: 'user1', nickname: '坐席1' },
      { id: 4, username: 'user2', nickname: '坐席2' }
    ]
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  }
}

// 获取日志列表
const getLogList = async () => {
  loading.value = true
  try {
    if (dateRange.value && dateRange.value.length === 2) {
      queryParams.start_time = dateRange.value[0]
      queryParams.end_time = dateRange.value[1]
    } else {
      queryParams.start_time = ''
      queryParams.end_time = ''
    }

    // 模拟数据
    logList.value = [
      {
        id: 1,
        user_id: 1,
        user_name: '超级管理员',
        user_ip: '192.168.1.100',
        user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        module: 'system',
        operation_type: 'login',
        operation_desc: '用户登录系统',
        request_url: '/api/v1/auth/login',
        request_method: 'POST',
        status: 1,
        duration: 120,
        error_msg: '',
        request_params: { username: 'admin', password: '******' },
        response_data: { code: 200, message: '登录成功', data: { token: '******' } },
        created_at: '2024-05-13 10:30:00'
      },
      {
        id: 2,
        user_id: 3,
        user_name: '坐席1',
        user_ip: '192.168.1.101',
        user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        module: 'customer',
        operation_type: 'create',
        operation_desc: '新增客户：张三',
        request_url: '/api/v1/customer/create',
        request_method: 'POST',
        status: 1,
        duration: 85,
        error_msg: '',
        request_params: { name: '张三', phone: '13800138000', company: '测试公司' },
        response_data: { code: 200, message: '创建成功', data: { id: 1001 } },
        created_at: '2024-05-13 10:25:00'
      },
      {
        id: 3,
        user_id: 2,
        user_name: '部门经理',
        user_ip: '192.168.1.102',
        user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15',
        module: 'report',
        operation_type: 'export',
        operation_desc: '导出坐席绩效报表',
        request_url: '/api/v1/report/agent/export',
        request_method: 'GET',
        status: 1,
        duration: 2560,
        error_msg: '',
        request_params: { start_date: '2024-05-01', end_date: '2024-05-13' },
        response_data: { code: 200, message: '导出成功' },
        created_at: '2024-05-13 10:20:00'
      },
      {
        id: 4,
        user_id: 4,
        user_name: '坐席2',
        user_ip: '192.168.1.103',
        user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/124.0.0.0 Safari/537.36',
        module: 'call',
        operation_type: 'query',
        operation_desc: '查询通话记录列表',
        request_url: '/api/v1/call/record/list',
        request_method: 'GET',
        status: 2,
        duration: 35,
        error_msg: '数据库连接超时',
        request_params: { page: 1, page_size: 20 },
        response_data: { code: 500, message: '数据库连接超时' },
        created_at: '2024-05-13 10:15:00'
      }
    ]
    total.value = 4

    // 更新统计数据
    statistics.total_count = 1256
    statistics.success_count = 1200
    statistics.fail_count = 56
    statistics.today_count = 36
  } catch (error) {
    ElMessage.error('获取日志列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleQuery = () => {
  queryParams.page = 1
  getLogList()
}

// 重置
const resetQuery = () => {
  queryFormRef.value?.resetFields()
  dateRange.value = []
  handleQuery()
}

// 导出日志
const handleExport = () => {
  ElMessage.info('导出功能开发中')
}

// 清空日志
const handleClear = () => {
  clearConfirm.value = false
  clearDialogVisible.value = true
}

// 确认清空
const confirmClear = async () => {
  if (!clearConfirm.value) {
    ElMessage.warning('请确认您了解此操作的风险')
    return
  }

  clearLoading.value = true
  try {
    // 这里调用API清空日志
    ElMessage.success('操作日志已清空')
    clearDialogVisible.value = false
    getLogList()
  } catch (error) {
    ElMessage.error(error.message || '清空失败')
  } finally {
    clearLoading.value = false
  }
}

// 查看详情
const viewDetail = (row) => {
  currentLog.value = row
  detailDialogVisible.value = true
}

// 格式化JSON
const formatJson = (json) => {
  if (!json) return '-'
  try {
    return JSON.stringify(typeof json === 'string' ? JSON.parse(json) : json, null, 2)
  } catch (e) {
    return String(json)
  }
}

// 获取模块标签类型
const getModuleTagType = (module) => {
  const typeMap = {
    'system': 'danger',
    'user': 'primary',
    'role': 'warning',
    'permission': 'info',
    'customer': 'success',
    'call': 'primary',
    'report': 'warning',
    'config': 'info'
  }
  return typeMap[module] || ''
}

// 获取模块名称
const getModuleName = (module) => {
  const nameMap = {
    'system': '系统管理',
    'user': '用户管理',
    'role': '角色管理',
    'permission': '权限管理',
    'customer': '客户管理',
    'call': '呼叫中心',
    'report': '统计报表',
    'config': '配置管理'
  }
  return nameMap[module] || module
}

// 获取操作类型标签类型
const getOperationTypeTagType = (type) => {
  const typeMap = {
    'login': 'success',
    'logout': 'info',
    'create': 'primary',
    'update': 'warning',
    'delete': 'danger',
    'query': 'info',
    'import': 'warning',
    'export': 'success',
    'upload': 'primary',
    'download': 'success',
    'other': ''
  }
  return typeMap[type] || ''
}

// 获取操作类型名称
const getOperationTypeName = (type) => {
  const nameMap = {
    'login': '登录',
    'logout': '登出',
    'create': '新增',
    'update': '编辑',
    'delete': '删除',
    'query': '查询',
    'import': '导入',
    'export': '导出',
    'upload': '上传',
    'download': '下载',
    'other': '其他'
  }
  return nameMap[type] || type
}

// 获取请求方法标签类型
const getMethodTagType = (method) => {
  const typeMap = {
    'GET': 'success',
    'POST': 'primary',
    'PUT': 'warning',
    'DELETE': 'danger',
    'PATCH': 'info',
    'OPTIONS': ''
  }
  return typeMap[method] || ''
}

onMounted(() => {
  getUserList()
  getLogList()
})
</script>

<style lang="scss" scoped>
.logs-manage-container {
  .stat-item {
    text-align: center;
    padding: 20px;
    background: #f5f7fa;
    border-radius: 8px;

    &.success .stat-value {
      color: #67c23a;
    }

    &.danger .stat-value {
      color: #f56c6c;
    }

    &.warning .stat-value {
      color: #e6a23c;
    }

    .stat-value {
      font-size: 32px;
      font-weight: bold;
      margin-bottom: 10px;
    }

    .stat-label {
      font-size: 14px;
      color: #909399;
    }
  }

  .log-detail {
    .code-block {
      background: #f5f7fa;
      padding: 15px;
      border-radius: 4px;
      overflow-x: auto;
      font-family: 'Courier New', Courier, monospace;
      font-size: 13px;
      line-height: 1.5;
      max-height: 400px;
      overflow-y: auto;

      &.error {
        background: #fef0f0;
        color: #f56c6c;
      }
    }
  }
}
</style>
