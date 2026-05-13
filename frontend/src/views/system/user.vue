<template>
  <div class="user-manage-container">
    <!-- 搜索区域 -->
    <div class="common-card">
      <el-form :model="queryParams" ref="queryFormRef" :inline="true" label-width="80px">
        <el-form-item label="用户名" prop="keyword">
          <el-input
            v-model="queryParams.keyword"
            placeholder="用户名/昵称/手机号"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select
            v-model="queryParams.status"
            placeholder="全部状态"
            clearable
            style="width: 120px"
          >
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="role_id">
          <el-select
            v-model="queryParams.role_id"
            placeholder="全部角色"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="role in roleList"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="部门" prop="department_id">
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
            新增用户
          </el-button>
          <el-button type="success" @click="handleImport">
            <el-icon><Upload /></el-icon>
            导入用户
          </el-button>
          <el-button type="info" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出用户
          </el-button>
          <el-button type="danger" @click="handleBatchDelete" :disabled="selectedIds.length === 0">
            <el-icon><Delete /></el-icon>
            批量删除
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 表格区域 -->
    <div class="common-card">
      <el-table
        v-loading="loading"
        :data="userList"
        @selection-change="handleSelectionChange"
        border
        stripe
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="avatar" label="头像" width="80" align="center">
          <template #default="scope">
            <el-avatar :size="40" :src="scope.row.avatar">
              {{ scope.row.nickname?.charAt(0) || scope.row.username.charAt(0) }}
            </el-avatar>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="nickname" label="昵称" width="120" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
        <el-table-column prop="department_name" label="部门" width="120" />
        <el-table-column prop="role_names" label="角色" min-width="150" show-overflow-tooltip>
          <template #default="scope">
            <el-tag
              v-for="role in scope.row.roles || []"
              :key="role.id"
              :type="getRoleTagType(role.id)"
              size="small"
              class="mr-1 mb-1"
            >
              {{ role.name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_superuser" label="管理员" width="100" align="center">
          <template #default="scope">
            <el-tag type="danger" size="small" v-if="scope.row.is_superuser">是</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'" size="small">
              {{ scope.row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_login" label="最后登录" width="160" align="center">
          <template #default="scope">
            {{ scope.row.last_login || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" align="center" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              text
              size="small"
              @click="handleEdit(scope.row)"
            >
              编辑
            </el-button>
            <el-button
              type="success"
              text
              size="small"
              @click="handleResetPassword(scope.row)"
            >
              重置密码
            </el-button>
            <el-button
              :type="scope.row.status === 1 ? 'warning' : 'success'"
              text
              size="small"
              @click="toggleStatus(scope.row)"
            >
              {{ scope.row.status === 1 ? '禁用' : '启用' }}
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
          :page-sizes="[10, 20, 30, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleQuery"
          @current-change="handleQuery"
        />
      </div>
    </div>

    <!-- 新增/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      destroy-on-close
    >
      <el-form :model="userForm" ref="userFormRef" label-width="100px" :rules="rules">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="userForm.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!currentUser">
          <el-input type="password" v-model="userForm.password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="部门" prop="department_id">
          <el-select
            v-model="userForm.department_id"
            placeholder="请选择部门"
            style="width: 100%"
          >
            <el-option
              v-for="dept in departmentList"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="role_ids">
          <el-select
            v-model="userForm.role_ids"
            multiple
            placeholder="请选择角色"
            style="width: 100%"
          >
            <el-option
              v-for="role in roleList"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="userForm.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="2">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="超级管理员" prop="is_superuser">
          <el-switch v-model="userForm.is_superuser" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="userForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUser" :loading="saveLoading">保存</el-button>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog
      v-model="resetPasswordVisible"
      title="重置密码"
      width="500px"
    >
      <el-form :model="resetPasswordForm" ref="resetPasswordFormRef" label-width="100px" :rules="resetPasswordRules">
        <el-form-item label="新密码" prop="new_password">
          <el-input type="password" v-model="resetPasswordForm.new_password" placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input type="password" v-model="resetPasswordForm.confirm_password" placeholder="请再次输入密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetPasswordVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmResetPassword" :loading="resetLoading">确认重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Upload, Download, Delete } from '@element-plus/icons-vue'

const loading = ref(false)
const queryFormRef = ref(null)
const userFormRef = ref(null)
const resetPasswordFormRef = ref(null)
const userList = ref([])
const roleList = ref([])
const departmentList = ref([])
const total = ref(0)
const dialogVisible = ref(false)
const resetPasswordVisible = ref(false)
const currentUser = ref(null)
const saveLoading = ref(false)
const resetLoading = ref(false)
const selectedIds = ref([])

// 查询参数
const queryParams = reactive({
  page: 1,
  page_size: 20,
  keyword: '',
  status: null,
  role_id: null,
  department_id: null
})

// 表单初始值
const initUserForm = {
  username: '',
  nickname: '',
  phone: '',
  email: '',
  password: '',
  department_id: null,
  role_ids: [],
  status: 1,
  is_superuser: false,
  remark: ''
}

const userForm = reactive({ ...initUserForm })

// 重置密码表单
const resetPasswordForm = reactive({
  user_id: null,
  new_password: '',
  confirm_password: ''
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3到20个字符之间', trigger: 'blur' }
  ],
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3456789]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在6到20个字符之间', trigger: 'blur' }
  ],
  department_id: [
    { required: true, message: '请选择部门', trigger: 'change' }
  ],
  role_ids: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

// 重置密码验证规则
const resetPasswordRules = {
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在6到20个字符之间', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== resetPasswordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const dialogTitle = computed(() => currentUser.value ? '编辑用户' : '新增用户')

// 获取角色标签类型
const getRoleTagType = (roleId) => {
  const types = ['success', 'warning', 'info', 'primary', 'danger']
  return types[roleId % types.length]
}

// 获取用户列表
const getUserList = async () => {
  loading.value = true
  try {
    // 模拟数据
    userList.value = [
      {
        id: 1,
        username: 'admin',
        nickname: '超级管理员',
        phone: '13800138000',
        email: 'admin@example.com',
        avatar: '',
        department_name: '总经办',
        roles: [{ id: 1, name: '超级管理员' }],
        role_names: '超级管理员',
        is_superuser: true,
        status: 1,
        last_login: '2024-05-13 10:30:00',
        created_at: '2023-01-01 00:00:00',
        remark: '系统超级管理员'
      },
      {
        id: 2,
        username: 'manager',
        nickname: '部门经理',
        phone: '13800138001',
        email: 'manager@example.com',
        avatar: '',
        department_name: '销售部',
        roles: [{ id: 2, name: '部门经理' }, { id: 3, name: '坐席' }],
        role_names: '部门经理,坐席',
        is_superuser: false,
        status: 1,
        last_login: '2024-05-13 09:20:00',
        created_at: '2023-01-02 00:00:00',
        remark: '销售部经理'
      },
      {
        id: 3,
        username: 'user1',
        nickname: '坐席1',
        phone: '13800138002',
        email: 'user1@example.com',
        avatar: '',
        department_name: '销售部',
        roles: [{ id: 3, name: '坐席' }],
        role_names: '坐席',
        is_superuser: false,
        status: 1,
        last_login: '2024-05-12 18:30:00',
        created_at: '2023-01-03 00:00:00',
        remark: '普通坐席'
      },
      {
        id: 4,
        username: 'user2',
        nickname: '坐席2',
        phone: '13800138003',
        email: 'user2@example.com',
        avatar: '',
        department_name: '客服部',
        roles: [{ id: 3, name: '坐席' }],
        role_names: '坐席',
        is_superuser: false,
        status: 2,
        last_login: '2024-05-10 15:20:00',
        created_at: '2023-01-04 00:00:00',
        remark: '已离职'
      }
    ]
    total.value = 4
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 获取角色列表
const getRoleList = async () => {
  // 模拟数据
  roleList.value = [
    { id: 1, name: '超级管理员' },
    { id: 2, name: '部门经理' },
    { id: 3, name: '坐席' },
    { id: 4, name: '质检员' },
    { id: 5, name: '财务' }
  ]
}

// 获取部门列表
const getDepartmentList = async () => {
  // 模拟数据
  departmentList.value = [
    { id: 1, name: '总经办' },
    { id: 2, name: '销售部' },
    { id: 3, name: '客服部' },
    { id: 4, name: '财务部' },
    { id: 5, name: '技术部' }
  ]
}

// 搜索
const handleQuery = () => {
  queryParams.page = 1
  getUserList()
}

// 重置
const resetQuery = () => {
  queryFormRef.value?.resetFields()
  handleQuery()
}

// 选择项变化
const handleSelectionChange = (val) => {
  selectedIds.value = val.map(item => item.id)
}

// 新增用户
const handleCreate = () => {
  currentUser.value = null
  Object.assign(userForm, initUserForm)
  dialogVisible.value = true
}

// 编辑用户
const handleEdit = (row) => {
  currentUser.value = row
  Object.assign(userForm, {
    username: row.username,
    nickname: row.nickname,
    phone: row.phone,
    email: row.email,
    password: '',
    department_id: row.department_id,
    role_ids: row.roles.map(r => r.id),
    status: row.status,
    is_superuser: row.is_superuser,
    remark: row.remark
  })
  dialogVisible.value = true
}

// 保存用户
const saveUser = async () => {
  if (!userFormRef.value) return

  await userFormRef.value.validate(async (valid) => {
    if (!valid) return

    saveLoading.value = true
    try {
      // 这里调用API保存用户
      ElMessage.success(currentUser.value ? '用户更新成功' : '用户创建成功')
      dialogVisible.value = false
      getUserList()
    } catch (error) {
      ElMessage.error(error.message || '保存失败')
    } finally {
      saveLoading.value = false
    }
  })
}

// 重置密码
const handleResetPassword = (row) => {
  resetPasswordForm.user_id = row.id
  resetPasswordForm.new_password = ''
  resetPasswordForm.confirm_password = ''
  resetPasswordVisible.value = true
}

// 确认重置密码
const confirmResetPassword = async () => {
  if (!resetPasswordFormRef.value) return

  await resetPasswordFormRef.value.validate(async (valid) => {
    if (!valid) return

    resetLoading.value = true
    try {
      // 这里调用API重置密码
      ElMessage.success('密码重置成功')
      resetPasswordVisible.value = false
    } catch (error) {
      ElMessage.error(error.message || '重置失败')
    } finally {
      resetLoading.value = false
    }
  })
}

// 切换状态
const toggleStatus = async (row) => {
  try {
    const action = row.status === 1 ? '禁用' : '启用'
    await ElMessageBox.confirm(
      `确定要${action}用户 "${row.nickname}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 这里调用API切换状态
    ElMessage.success(`用户已${action}`)
    getUserList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败')
    }
  }
}

// 删除用户
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${row.nickname}" 吗？删除后无法恢复`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 这里调用API删除用户
    ElMessage.success('用户删除成功')
    getUserList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 批量删除
const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedIds.value.length} 个用户吗？删除后无法恢复`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 这里调用API批量删除用户
    ElMessage.success('批量删除成功')
    getUserList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 导入用户
const handleImport = () => {
  ElMessage.info('导入功能开发中')
}

// 导出用户
const handleExport = () => {
  ElMessage.info('导出功能开发中')
}

onMounted(() => {
  getUserList()
  getRoleList()
  getDepartmentList()
})
</script>

<style lang="scss" scoped>
.user-manage-container {
}
</style>
