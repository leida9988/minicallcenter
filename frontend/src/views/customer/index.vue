<template>
  <div class="customer-container">
    <!-- 搜索区域 -->
    <div class="common-card">
      <el-form :model="queryParams" ref="queryFormRef" :inline="true" label-width="80px">
        <el-form-item label="客户姓名" prop="keyword">
          <el-input
            v-model="queryParams.keyword"
            placeholder="请输入姓名/手机号/公司"
            clearable
            style="width: 240px"
          />
        </el-form-item>
        <el-form-item label="客户状态" prop="status">
          <el-select
            v-model="queryParams.status"
            placeholder="请选择客户状态"
            clearable
            style="width: 200px"
          >
            <el-option label="全部" :value="null" />
            <el-option label="待联系" :value="1" />
            <el-option label="联系中" :value="2" />
            <el-option label="有意向" :value="3" />
            <el-option label="已成交" :value="4" />
            <el-option label="已拒绝" :value="5" />
            <el-option label="无效客户" :value="6" />
          </el-select>
        </el-form-item>
        <el-form-item label="客户等级" prop="level">
          <el-select
            v-model="queryParams.level"
            placeholder="请选择客户等级"
            clearable
            style="width: 200px"
          >
            <el-option label="全部" :value="null" />
            <el-option label="普通" :value="1" />
            <el-option label="VIP" :value="2" />
            <el-option label="重要客户" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签" prop="tags">
          <el-select
            v-model="queryParams.tags"
            placeholder="请选择标签"
            multiple
            clearable
            style="width: 240px"
          >
            <el-option
              v-for="tag in tagList"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
              :style="{ color: tag.color }"
            />
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
            新增客户
          </el-button>
          <el-button type="success" @click="handleImport">
            <el-icon><Upload /></el-icon>
            导入客户
          </el-button>
          <el-button type="info" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出客户
          </el-button>
          <el-button type="warning" @click="handleBatchAssign" :disabled="selectedIds.length === 0">
            <el-icon><UserFilled /></el-icon>
            批量分配
          </el-button>
          <el-button type="danger" @click="handleBatchRecycle" :disabled="selectedIds.length === 0">
            <el-icon><Delete /></el-icon>
            批量回收
          </el-button>
        </el-col>
      </el-row>
    </div>
    <!-- 表格区域 -->
    <div class="common-card">
      <el-table
        v-loading="loading"
        :data="customerList"
        @selection-change="handleSelectionChange"
        border
        stripe
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column prop="name" label="客户姓名" width="120" />
        <el-table-column prop="phone" label="手机号码" width="150">
          <template #default="scope">
            <el-button
              type="text"
              class="phone-number"
              @click="handleCall(scope.row)"
            >
              <el-icon><Phone /></el-icon>
              {{ scope.row.phone }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="gender" label="性别" width="80" align="center">
          <template #default="scope">
            <span v-if="scope.row.gender === 1">男</span>
            <span v-else-if="scope.row.gender === 2">女</span>
            <span v-else>未知</span>
          </template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="80" align="center" />
        <el-table-column prop="company" label="公司名称" show-overflow-tooltip />
        <el-table-column prop="level" label="客户等级" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getLevelTagType(scope.row.level)" size="small">
              {{ getLevelText(scope.row.level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="客户状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)" size="small">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tags" label="客户标签" min-width="120">
          <template #default="scope">
            <el-tag
              v-for="tag in scope.row.tags || []"
              :key="tag"
              size="small"
              style="margin-right: 5px; margin-bottom: 2px"
            >
              {{ tag }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="follow_count" label="跟进次数" width="90" align="center" />
        <el-table-column prop="total_call_duration" label="通话时长" width="100" align="center">
          <template #default="scope">
            {{ formatDuration(scope.row.total_call_duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="assign_user_name" label="所属坐席" width="100" />
        <el-table-column prop="last_follow_time" label="最后跟进" width="160" />
        <el-table-column prop="next_follow_time" label="下次跟进" width="160" />
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              text
              size="small"
              @click="handleCall(scope.row)"
            >
              外呼
            </el-button>
            <el-button
              type="success"
              text
              size="small"
              @click="handleFollow(scope.row)"
            >
              跟进
            </el-button>
            <el-button
              type="info"
              text
              size="small"
              @click="handleDetail(scope.row)"
            >
              详情
            </el-button>
            <el-button
              type="warning"
              text
              size="small"
              @click="handleEdit(scope.row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              text
              size="small"
              @click="handleDelete(scope.row)"
            >
              删除
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
    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      destroy-on-close
    >
      <customer-form
        ref="customerFormRef"
        :customer-id="currentCustomerId"
        @success="handleQuery"
      />
    </el-dialog>
    <!-- 跟进记录对话框 -->
    <el-dialog
      v-model="followDialogVisible"
      title="跟进记录"
      width="800px"
      destroy-on-close
    >
      <follow-record :customer-id="currentCustomerId" />
    </el-dialog>
    <!-- 批量分配对话框 -->
    <el-dialog
      v-model="assignDialogVisible"
      title="批量分配客户"
      width="500px"
    >
      <el-form label-width="80px">
        <el-form-item label="分配给" required>
          <el-select
          v-model="assignUserId" placeholder="请选择坐席" style="width: 100%">
            <el-option
              v-for="user in userList"
              :key="user.id"
              :label="user.nickname || user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmBatchAssign" :loading="assignLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import CustomerForm from './components/CustomerForm.vue'
import FollowRecord from './components/FollowRecord.vue'
import {
  getCustomerListApi,
  deleteCustomerApi,
  batchRecycleCustomerApi,
  assignCustomerApi
} from '@/api/customer'
import { getUserListApi } from '@/api/user'
import { formatDuration } from '@/utils/datetime'
const router = useRouter()
const loading = ref(false)
const queryFormRef = ref(null)
const customerFormRef = ref(null)
const customerList = ref([])
const total = ref(0)
const selectedIds = ref([])
const tagList = ref([])
const userList = ref([])
const dateRange = ref([])
// 查询参数
const queryParams = reactive({
  page: 1,
  page_size: 20,
  keyword: '',
  status: null,
  level: null,
  tags: [],
  start_time: '',
  end_time: ''
})
// 对话框相关
const dialogVisible = ref(false)
const followDialogVisible = ref(false)
const assignDialogVisible = ref(false)
const currentCustomerId = ref(null)
const assignLoading = ref(false)
const assignUserId = ref(null)
const dialogTitle = computed(() => currentCustomerId.value ? '编辑客户' : '新增客户')
// 获取客户列表
const getCustomerList = async () => {
  loading.value = true
  try {
    if (dateRange.value && dateRange.value.length === 2) {
      queryParams.start_time = dateRange.value[0]
      queryParams.end_time = dateRange.value[1]
    } else {
      queryParams.start_time = ''
      queryParams.end_time = ''
    }
    const res = await getCustomerListApi(queryParams)
    customerList.value = res.data.list
    total.value = res.data.total
  } catch (error) {
    ElMessage.error(error.message || '获取客户列表失败')
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
  getCustomerList()
}
// 重置
const resetQuery = () => {
  queryFormRef.value?.resetFields()
  dateRange.value = []
  handleQuery()
}
// 选择项变化
const handleSelectionChange = (val) => {
  selectedIds.value = val.map(item => item.id)
}
// 新增客户
const handleCreate = () => {
  currentCustomerId.value = null
  dialogVisible.value = true
}
// 编辑客户
const handleEdit = (row) => {
  currentCustomerId.value = row.id
  dialogVisible.value = true
}
// 客户详情
const handleDetail = (row) => {
  router.push(`/customer/${row.id}`)
}
// 外呼客户
const handleCall = (row) => {
  // 跳转到呼叫中心页面，携带客户信息
  ElMessage.success(`正在呼叫 ${row.name} - ${row.phone}`)
  // 可以通过路由传参，在呼叫中心页面自动填充号码
  router.push({
    name: 'Call',
    query: {
      phone: row.phone,
      customerId: row.id,
      customerName: row.name
    }
  })
}
// 跟进客户
const handleFollow = (row) => {
  currentCustomerId.value = row.id
  followDialogVisible.value = true
}
// 删除客户
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除客户 "${row.name}" 吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteCustomerApi(row.id)
      ElMessage.success('删除成功')
      handleQuery()
    } catch (error) {
      ElMessage.error(error.message || '删除失败')
    }
  })
}
// 批量分配客户
const handleBatchAssign = () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择要分配的客户')
    return
  }
  assignDialogVisible.value = true
}
// 确认批量分配
const confirmBatchAssign = async () => {
  if (!assignUserId.value) {
    ElMessage.warning('请选择要分配的坐席')
    return
  }
  assignLoading.value = true
  try {
    await assignCustomerApi({
      customer_ids: selectedIds.value,
      user_id: assignUserId.value
    })
    ElMessage.success('分配成功')
    assignDialogVisible.value = false
    assignUserId.value = null
    handleQuery()
  } catch (error) {
    ElMessage.error(error.message || '分配失败')
  } finally {
    assignLoading.value = false
  }
}
// 批量回收客户
const handleBatchRecycle = () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择要回收的客户')
    return
  }
  ElMessageBox.confirm(
    `确定要回收选中的 ${selectedIds.value.length} 个客户到公海吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await batchRecycleCustomerApi({ customer_ids: selectedIds.value })
      ElMessage.success('回收成功')
      handleQuery()
    } catch (error) {
      ElMessage.error(error.message || '回收失败')
    }
  })
}
// 导入客户
const handleImport = () => {
  ElMessage.info('导入功能开发中')
}
// 导出客户
const handleExport = () => {
  ElMessage.info('导出功能开发中')
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
onMounted(() => {
  getCustomerList()
  getUserList()
})
</script>
<style lang="scss" scoped>
.customer-container {
}
</style>
