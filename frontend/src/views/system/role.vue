<template>
  <div class="role-manage-container">
    <!-- 搜索区域 -->
    <div class="common-card">
      <el-form :model="queryParams" ref="queryFormRef" :inline="true" label-width="80px">
        <el-form-item label="角色名称" prop="keyword">
          <el-input
            v-model="queryParams.keyword"
            placeholder="请输入角色名称"
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
            新增角色
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 表格区域 -->
    <div class="common-card">
      <el-table
        v-loading="loading"
        :data="roleList"
        border
        stripe
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="name" label="角色名称" width="150" />
        <el-table-column prop="code" label="角色标识" width="150" />
        <el-table-column prop="description" label="角色描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="user_count" label="关联用户" width="120" align="center" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'" size="small">
              {{ scope.row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" align="center" />
        <el-table-column label="操作" width="220" fixed="right">
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
              @click="handlePermission(scope.row)"
            >
              分配权限
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
              :disabled="scope.row.user_count > 0 || scope.row.is_system"
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

    <!-- 新增/编辑角色对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      destroy-on-close
    >
      <el-form :model="roleForm" ref="roleFormRef" label-width="100px" :rules="rules">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="roleForm.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色标识" prop="code">
          <el-input v-model="roleForm.code" placeholder="请输入角色标识，如：admin" />
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="roleForm.sort" :min="0" :max="9999" style="width: 100%" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="roleForm.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="2">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="角色描述">
          <el-input
            v-model="roleForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入角色描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRole" :loading="saveLoading">保存</el-button>
      </template>
    </el-dialog>

    <!-- 分配权限对话框 -->
    <el-dialog
      v-model="permissionDialogVisible"
      title="分配权限"
      width="700px"
      destroy-on-close
    >
      <el-tree
        ref="permissionTreeRef"
        :data="permissionTree"
        :props="treeProps"
        show-checkbox
        node-key="id"
        :default-checked-keys="checkedPermissionIds"
        :expand-on-click-node="false"
        check-strictly
      >
        <template #default="{ node, data }">
          <span class="custom-tree-node">
            <el-icon class="mr-1" v-if="data.type === 1"><Menu /></el-icon>
            <el-icon class="mr-1" v-if="data.type === 2"><Operation /></el-icon>
            <el-icon class="mr-1" v-if="data.type === 3"><Key /></el-icon>
            <span>{{ data.name }}</span>
            <el-tag size="small" type="info" class="ml-2" v-if="data.type === 1">菜单</el-tag>
            <el-tag size="small" type="warning" class="ml-2" v-if="data.type === 2">按钮</el-tag>
            <el-tag size="small" type="danger" class="ml-2" v-if="data.type === 3">API</el-tag>
          </span>
        </template>
      </el-tree>
      <template #footer>
        <el-button @click="permissionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePermission" :loading="permissionLoading">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Menu, Operation, Key } from '@element-plus/icons-vue'

const loading = ref(false)
const queryFormRef = ref(null)
const roleFormRef = ref(null)
const permissionTreeRef = ref(null)
const roleList = ref([])
const permissionTree = ref([])
const total = ref(0)
const dialogVisible = ref(false)
const permissionDialogVisible = ref(false)
const currentRole = ref(null)
const saveLoading = ref(false)
const permissionLoading = ref(false)
const checkedPermissionIds = ref([])

// 查询参数
const queryParams = reactive({
  page: 1,
  page_size: 20,
  keyword: '',
  status: null
})

// 表单初始值
const initRoleForm = {
  name: '',
  code: '',
  sort: 0,
  status: 1,
  description: ''
}

const roleForm = reactive({ ...initRoleForm })

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 20, message: '角色名称长度在2到20个字符之间', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入角色标识', trigger: 'blur' },
    { pattern: /^[a-zA-Z_]+$/, message: '角色标识只能包含字母和下划线', trigger: 'blur' }
  ]
}

// 树节点配置
const treeProps = {
  children: 'children',
  label: 'name'
}

const dialogTitle = computed(() => currentRole.value ? '编辑角色' : '新增角色')

// 获取角色列表
const getRoleList = async () => {
  loading.value = true
  try {
    // 模拟数据
    roleList.value = [
      {
        id: 1,
        name: '超级管理员',
        code: 'super_admin',
        description: '系统超级管理员，拥有所有权限',
        sort: 0,
        user_count: 1,
        status: 1,
        is_system: true,
        created_at: '2023-01-01 00:00:00'
      },
      {
        id: 2,
        name: '部门经理',
        code: 'manager',
        description: '部门经理，拥有部门数据管理权限',
        sort: 1,
        user_count: 5,
        status: 1,
        is_system: false,
        created_at: '2023-01-02 00:00:00'
      },
      {
        id: 3,
        name: '坐席',
        code: 'agent',
        description: '普通坐席，拥有客户和呼叫功能权限',
        sort: 2,
        user_count: 45,
        status: 1,
        is_system: false,
        created_at: '2023-01-03 00:00:00'
      },
      {
        id: 4,
        name: '质检员',
        code: 'inspector',
        description: '质检员，拥有呼叫记录查看和质检权限',
        sort: 3,
        user_count: 3,
        status: 1,
        is_system: false,
        created_at: '2023-01-04 00:00:00'
      },
      {
        id: 5,
        name: '财务',
        code: 'finance',
        description: '财务人员，拥有报表和对账权限',
        sort: 4,
        user_count: 2,
        status: 2,
        is_system: false,
        created_at: '2023-01-05 00:00:00'
      }
    ]
    total.value = 5
  } catch (error) {
    ElMessage.error('获取角色列表失败')
  } finally {
    loading.value = false
  }
}

// 获取权限树
const getPermissionTree = async () => {
  // 模拟数据
  permissionTree.value = [
    {
      id: 1,
      name: '首页',
      type: 1,
      permission: 'dashboard:view',
      children: []
    },
    {
      id: 2,
      name: '客户管理',
      type: 1,
      permission: 'customer:view',
      children: [
        { id: 21, name: '客户列表', type: 1, permission: 'customer:list', children: [] },
        { id: 22, name: '新增客户', type: 2, permission: 'customer:create', children: [] },
        { id: 23, name: '编辑客户', type: 2, permission: 'customer:update', children: [] },
        { id: 24, name: '删除客户', type: 2, permission: 'customer:delete', children: [] },
        { id: 25, name: '导入导出', type: 2, permission: 'customer:import_export', children: [] },
        { id: 26, name: '客户详情', type: 1, permission: 'customer:detail', children: [] },
        { id: 27, name: '添加跟进', type: 2, permission: 'customer:add_follow', children: [] }
      ]
    },
    {
      id: 3,
      name: '呼叫中心',
      type: 1,
      permission: 'call:view',
      children: [
        { id: 31, name: '外呼页面', type: 1, permission: 'call:agent', children: [] },
        { id: 32, name: '外呼操作', type: 2, permission: 'call:make', children: [] },
        { id: 33, name: '通话记录', type: 1, permission: 'call:record', children: [] },
        { id: 34, name: '播放录音', type: 2, permission: 'call:play_recording', children: [] },
        { id: 35, name: '下载录音', type: 2, permission: 'call:download_recording', children: [] },
        { id: 36, name: '呼叫任务', type: 1, permission: 'call:task', children: [] },
        { id: 37, name: '话术管理', type: 1, permission: 'call:script', children: [] }
      ]
    },
    {
      id: 4,
      name: '统计报表',
      type: 1,
      permission: 'report:view',
      children: [
        { id: 41, name: '通话趋势', type: 1, permission: 'report:call_trend', children: [] },
        { id: 42, name: '坐席绩效', type: 1, permission: 'report:agent_performance', children: [] },
        { id: 43, name: '客户分析', type: 1, permission: 'report:customer_analysis', children: [] }
      ]
    },
    {
      id: 5,
      name: '系统管理',
      type: 1,
      permission: 'system:view',
      children: [
        { id: 51, name: '用户管理', type: 1, permission: 'system:user', children: [] },
        { id: 52, name: '新增用户', type: 2, permission: 'system:user:create', children: [] },
        { id: 53, name: '编辑用户', type: 2, permission: 'system:user:update', children: [] },
        { id: 54, name: '删除用户', type: 2, permission: 'system:user:delete', children: [] },
        { id: 55, name: '重置密码', type: 2, permission: 'system:user:reset_password', children: [] },
        { id: 56, name: '角色管理', type: 1, permission: 'system:role', children: [] },
        { id: 57, name: '权限管理', type: 1, permission: 'system:permission', children: [] },
        { id: 58, name: '系统配置', type: 1, permission: 'system:config', children: [] },
        { id: 59, name: '操作日志', type: 1, permission: 'system:logs', children: [] }
      ]
    }
  ]
}

// 搜索
const handleQuery = () => {
  queryParams.page = 1
  getRoleList()
}

// 重置
const resetQuery = () => {
  queryFormRef.value?.resetFields()
  handleQuery()
}

// 新增角色
const handleCreate = () => {
  currentRole.value = null
  Object.assign(roleForm, initRoleForm)
  dialogVisible.value = true
}

// 编辑角色
const handleEdit = (row) => {
  currentRole.value = row
  Object.assign(roleForm, {
    name: row.name,
    code: row.code,
    sort: row.sort,
    status: row.status,
    description: row.description
  })
  dialogVisible.value = true
}

// 保存角色
const saveRole = async () => {
  if (!roleFormRef.value) return

  await roleFormRef.value.validate(async (valid) => {
    if (!valid) return

    saveLoading.value = true
    try {
      // 这里调用API保存角色
      ElMessage.success(currentRole.value ? '角色更新成功' : '角色创建成功')
      dialogVisible.value = false
      getRoleList()
    } catch (error) {
      ElMessage.error(error.message || '保存失败')
    } finally {
      saveLoading.value = false
    }
  })
}

// 分配权限
const handlePermission = (row) => {
  currentRole.value = row
  checkedPermissionIds.value = [] // 这里应该加载该角色已有的权限ID
  permissionDialogVisible.value = true

  // 模拟加载已选权限
  setTimeout(() => {
    if (permissionTreeRef.value) {
      // 超级管理员默认拥有所有权限
      if (row.code === 'super_admin') {
        const allIds = getAllPermissionIds(permissionTree.value)
        permissionTreeRef.value.setCheckedKeys(allIds)
      } else {
        // 其他角色默认选一些权限
        permissionTreeRef.value.setCheckedKeys([1, 2, 21, 26, 3, 31, 33])
      }
    }
  }, 100)
}

// 递归获取所有权限ID
const getAllPermissionIds = (tree) => {
  let ids = []
  tree.forEach(item => {
    ids.push(item.id)
    if (item.children && item.children.length > 0) {
      ids = ids.concat(getAllPermissionIds(item.children))
    }
  })
  return ids
}

// 保存权限
const savePermission = async () => {
  if (!permissionTreeRef.value) return

  const checkedKeys = permissionTreeRef.value.getCheckedKeys()
  const halfCheckedKeys = permissionTreeRef.value.getHalfCheckedKeys()
  const allPermissionIds = [...checkedKeys, ...halfCheckedKeys]

  permissionLoading.value = true
  try {
    // 这里调用API保存权限
    ElMessage.success('权限分配成功')
    permissionDialogVisible.value = false
  } catch (error) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    permissionLoading.value = false
  }
}

// 切换状态
const toggleStatus = async (row) => {
  try {
    const action = row.status === 1 ? '禁用' : '启用'
    await ElMessageBox.confirm(
      `确定要${action}角色 "${row.name}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 这里调用API切换状态
    ElMessage.success(`角色已${action}`)
    getRoleList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败')
    }
  }
}

// 删除角色
const handleDelete = async (row) => {
  try {
    if (row.is_system) {
      ElMessage.error('系统内置角色无法删除')
      return
    }
    if (row.user_count > 0) {
      ElMessage.error('该角色下有关联用户，无法删除')
      return
    }

    await ElMessageBox.confirm(
      `确定要删除角色 "${row.name}" 吗？删除后无法恢复`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 这里调用API删除角色
    ElMessage.success('角色删除成功')
    getRoleList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

onMounted(() => {
  getRoleList()
  getPermissionTree()
})
</script>

<style lang="scss" scoped>
.role-manage-container {
  .custom-tree-node {
    display: flex;
    align-items: center;
    flex: 1;
    justify-content: space-between;
    font-size: 14px;
    padding-right: 8px;
  }
}
</style>
