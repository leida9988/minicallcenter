<template>
  <div class="permission-manage-container">
    <!-- 操作按钮 -->
    <div class="common-card">
      <el-row :gutter="10">
        <el-col :span="24">
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新增权限
          </el-button>
          <el-button type="success" @click="handleGenerate">
            <el-icon><Refresh /></el-icon>
            同步路由权限
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 权限树表格 -->
    <div class="common-card">
      <el-table
        v-loading="loading"
        :data="permissionTree"
        border
        stripe
        row-key="id"
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
        default-expand-all
      >
        <el-table-column prop="name" label="权限名称" min-width="200">
          <template #default="scope">
            <span class="flex items-center">
              <el-icon class="mr-1" v-if="scope.row.type === 1"><Menu /></el-icon>
              <el-icon class="mr-1" v-if="scope.row.type === 2"><Operation /></el-icon>
              <el-icon class="mr-1" v-if="scope.row.type === 3"><Key /></el-icon>
              {{ scope.row.name }}
              <el-tag size="small" type="info" class="ml-2" v-if="scope.row.type === 1">菜单</el-tag>
              <el-tag size="small" type="warning" class="ml-2" v-if="scope.row.type === 2">按钮</el-tag>
              <el-tag size="small" type="danger" class="ml-2" v-if="scope.row.type === 3">API</el-tag>
              <el-tag size="small" type="success" class="ml-2" v-if="scope.row.is_system">系统</el-tag>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="code" label="权限标识" min-width="250" show-overflow-tooltip />
        <el-table-column prop="path" label="路由路径/API路径" min-width="250" show-overflow-tooltip />
        <el-table-column prop="method" label="请求方法" width="100" align="center" v-if="showApiColumn">
          <template #default="scope">
            <el-tag :type="getMethodTagType(scope.row.method)" size="small" v-if="scope.row.type === 3">
              {{ scope.row.method }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="icon" label="图标" width="100" align="center" v-if="showMenuColumn">
          <template #default="scope">
            <el-icon v-if="scope.row.icon && scope.row.type === 1">
              <component :is="scope.row.icon" />
            </el-icon>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="sort" label="排序" width="100" align="center" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'" size="small">
              {{ scope.row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="权限描述" min-width="150" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="160" align="center" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              text
              size="small"
              @click="handleCreateChild(scope.row)"
              :disabled="scope.row.type === 3"
            >
              新增子项
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
              :disabled="scope.row.is_system || (scope.row.children && scope.row.children.length > 0)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新增/编辑权限对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      destroy-on-close
    >
      <el-form :model="permissionForm" ref="permissionFormRef" label-width="100px" :rules="rules">
        <el-form-item label="上级权限">
          <el-tree-select
            v-model="permissionForm.parent_id"
            :data="permissionTree"
            :props="treeProps"
            placeholder="请选择上级权限"
            style="width: 100%"
            check-strictly
            :default-expand-all="true"
          />
        </el-form-item>
        <el-form-item label="权限名称" prop="name">
          <el-input v-model="permissionForm.name" placeholder="请输入权限名称" />
        </el-form-item>
        <el-form-item label="权限标识" prop="code">
          <el-input v-model="permissionForm.code" placeholder="请输入权限标识，如：user:create" />
        </el-form-item>
        <el-form-item label="权限类型" prop="type">
          <el-radio-group v-model="permissionForm.type" @change="handleTypeChange">
            <el-radio :value="1">菜单</el-radio>
            <el-radio :value="2">按钮</el-radio>
            <el-radio :value="3">API接口</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="路由路径" v-if="permissionForm.type === 1" prop="path">
          <el-input v-model="permissionForm.path" placeholder="请输入路由路径，如：/system/user" />
        </el-form-item>
        <el-form-item label="组件路径" v-if="permissionForm.type === 1" prop="component">
          <el-input v-model="permissionForm.component" placeholder="请输入组件路径，如：system/user/index" />
        </el-form-item>
        <el-form-item label="路由名称" v-if="permissionForm.type === 1" prop="route_name">
          <el-input v-model="permissionForm.route_name" placeholder="请输入路由名称" />
        </el-form-item>
        <el-form-item label="图标" v-if="permissionForm.type === 1" prop="icon">
          <el-input v-model="permissionForm.icon" placeholder="请输入图标名称，如：User" />
        </el-form-item>
        <el-form-item label="API路径" v-if="permissionForm.type === 3" prop="path">
          <el-input v-model="permissionForm.path" placeholder="请输入API路径，如：GET /api/v1/user/list" />
        </el-form-item>
        <el-form-item label="请求方法" v-if="permissionForm.type === 3" prop="method">
          <el-select v-model="permissionForm.method" placeholder="请选择请求方法" style="width: 100%">
            <el-option label="GET" value="GET" />
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
            <el-option label="PATCH" value="PATCH" />
            <el-option label="OPTIONS" value="OPTIONS" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="permissionForm.sort" :min="0" :max="9999" style="width: 100px" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="permissionForm.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="2">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="其他配置" v-if="permissionForm.type === 1">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-checkbox v-model="permissionForm.is_visible">在菜单显示</el-checkbox>
            </el-col>
            <el-col :span="8">
              <el-checkbox v-model="permissionForm.is_keep_alive">路由缓存</el-checkbox>
            </el-col>
            <el-col :span="8">
              <el-checkbox v-model="permissionForm.is_external">外部链接</el-checkbox>
            </el-col>
          </el-row>
        </el-form-item>
        <el-form-item label="权限描述">
          <el-input
            v-model="permissionForm.description"
            type="textarea"
            :rows="2"
            placeholder="请输入权限描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePermission" :loading="saveLoading">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Menu, Operation, Key } from '@element-plus/icons-vue'

const loading = ref(false)
const permissionFormRef = ref(null)
const permissionTree = ref([])
const dialogVisible = ref(false)
const currentPermission = ref(null)
const saveLoading = ref(false)

// 表单初始值
const initPermissionForm = {
  parent_id: null,
  name: '',
  code: '',
  type: 1,
  path: '',
  component: '',
  route_name: '',
  icon: '',
  method: '',
  sort: 0,
  status: 1,
  is_visible: true,
  is_keep_alive: false,
  is_external: false,
  description: ''
}

const permissionForm = reactive({ ...initPermissionForm })

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入权限名称', trigger: 'blur' },
    { min: 2, max: 50, message: '权限名称长度在2到50个字符之间', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入权限标识', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_:]+$/, message: '权限标识只能包含字母、数字、下划线和冒号', trigger: 'blur' }
  ]
}

// 树节点配置
const treeProps = {
  children: 'children',
  label: 'name',
  value: 'id'
}

const dialogTitle = computed(() => currentPermission.value ? '编辑权限' : '新增权限')
const showApiColumn = ref(true)
const showMenuColumn = ref(true)

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

// 获取权限树
const getPermissionTree = async () => {
  loading.value = true
  try {
    // 模拟数据
    permissionTree.value = [
      {
        id: 1,
        name: '首页',
        code: 'dashboard:view',
        type: 1,
        path: '/dashboard',
        component: 'dashboard/index',
        route_name: 'Dashboard',
        icon: 'Odometer',
        sort: 0,
        status: 1,
        is_visible: true,
        is_keep_alive: false,
        is_external: false,
        is_system: true,
        description: '系统首页',
        created_at: '2023-01-01 00:00:00',
        children: []
      },
      {
        id: 2,
        name: '客户管理',
        code: 'customer:view',
        type: 1,
        path: '/customer',
        component: 'customer/index',
        route_name: 'Customer',
        icon: 'User',
        sort: 1,
        status: 1,
        is_visible: true,
        is_keep_alive: false,
        is_external: false,
        is_system: true,
        description: '客户管理菜单',
        created_at: '2023-01-01 00:00:00',
        children: [
          {
            id: 21,
            name: '客户列表',
            code: 'customer:list',
            type: 1,
            path: '/customer',
            component: 'customer/index',
            route_name: 'CustomerList',
            icon: 'List',
            sort: 0,
            status: 1,
            is_visible: true,
            is_keep_alive: true,
            is_external: false,
            is_system: true,
            description: '客户列表页面',
            created_at: '2023-01-01 00:00:00',
            children: [
              { id: 211, name: '新增客户', code: 'customer:create', type: 2, sort: 0, status: 1, description: '新增客户按钮', created_at: '2023-01-01 00:00:00' },
              { id: 212, name: '编辑客户', code: 'customer:update', type: 2, sort: 1, status: 1, description: '编辑客户按钮', created_at: '2023-01-01 00:00:00' },
              { id: 213, name: '删除客户', code: 'customer:delete', type: 2, sort: 2, status: 1, description: '删除客户按钮', created_at: '2023-01-01 00:00:00' },
              { id: 214, name: '导入客户', code: 'customer:import', type: 2, sort: 3, status: 1, description: '导入客户按钮', created_at: '2023-01-01 00:00:00' },
              { id: 215, name: '导出客户', code: 'customer:export', type: 2, sort: 4, status: 1, description: '导出客户按钮', created_at: '2023-01-01 00:00:00' }
            ]
          },
          {
            id: 22,
            name: '客户详情',
            code: 'customer:detail',
            type: 1,
            path: '/customer/:id',
            component: 'customer/detail',
            route_name: 'CustomerDetail',
            icon: 'Document',
            sort: 1,
            status: 1,
            is_visible: false,
            is_keep_alive: true,
            is_external: false,
            is_system: true,
            description: '客户详情页面',
            created_at: '2023-01-01 00:00:00',
            children: [
              { id: 221, name: '添加跟进', code: 'customer:add_follow', type: 2, sort: 0, status: 1, description: '添加跟进按钮', created_at: '2023-01-01 00:00:00' }
            ]
          }
        ]
      },
      {
        id: 3,
        name: '呼叫中心',
        code: 'call:view',
        type: 1,
        path: '/call',
        component: 'call/index',
        route_name: 'Call',
        icon: 'Phone',
        sort: 2,
        status: 1,
        is_visible: true,
        is_keep_alive: false,
        is_external: false,
        is_system: true,
        description: '呼叫中心菜单',
        created_at: '2023-01-01 00:00:00',
        children: [
          { id: 31, name: '外呼页面', code: 'call:agent', type: 1, path: '/call', component: 'call/index', route_name: 'CallAgent', icon: 'Phone', sort: 0, status: 1, is_visible: true, is_keep_alive: true, is_external: false, is_system: true, description: '坐席外呼页面', created_at: '2023-01-01 00:00:00', children: [] },
          { id: 32, name: '通话记录', code: 'call:record', type: 1, path: '/call/record', component: 'call/call-record', route_name: 'CallRecord', icon: 'Document', sort: 1, status: 1, is_visible: true, is_keep_alive: true, is_external: false, is_system: true, description: '通话记录页面', created_at: '2023-01-01 00:00:00', children: [] }
        ]
      },
      {
        id: 5,
        name: '系统管理',
        code: 'system:view',
        type: 1,
        path: '/system',
        component: 'system/index',
        route_name: 'System',
        icon: 'Setting',
        sort: 4,
        status: 1,
        is_visible: true,
        is_keep_alive: false,
        is_external: false,
        is_system: true,
        description: '系统管理菜单',
        created_at: '2023-01-01 00:00:00',
        children: [
          { id: 51, name: '用户管理', code: 'system:user', type: 1, path: '/system/user', component: 'system/user', route_name: 'SystemUser', icon: 'User', sort: 0, status: 1, is_visible: true, is_keep_alive: true, is_external: false, is_system: true, description: '用户管理页面', created_at: '2023-01-01 00:00:00', children: [] },
          { id: 52, name: '角色管理', code: 'system:role', type: 1, path: '/system/role', component: 'system/role', route_name: 'SystemRole', icon: 'Avatar', sort: 1, status: 1, is_visible: true, is_keep_alive: true, is_external: false, is_system: true, description: '角色管理页面', created_at: '2023-01-01 00:00:00', children: [] },
          { id: 53, name: '权限管理', code: 'system:permission', type: 1, path: '/system/permission', component: 'system/permission', route_name: 'SystemPermission', icon: 'Key', sort: 2, status: 1, is_visible: true, is_keep_alive: true, is_external: false, is_system: true, description: '权限管理页面', created_at: '2023-01-01 00:00:00', children: [] }
        ]
      }
    ]
  } catch (error) {
    ElMessage.error('获取权限树失败')
  } finally {
    loading.value = false
  }
}

// 权限类型变化
const handleTypeChange = () => {
  // 切换类型时清空相关字段
  permissionForm.path = ''
  permissionForm.component = ''
  permissionForm.route_name = ''
  permissionForm.icon = ''
  permissionForm.method = ''
}

// 新增权限
const handleCreate = () => {
  currentPermission.value = null
  Object.assign(permissionForm, initPermissionForm)
  dialogVisible.value = true
}

// 新增子权限
const handleCreateChild = (row) => {
  currentPermission.value = null
  Object.assign(permissionForm, initPermissionForm)
  permissionForm.parent_id = row.id
  // 子权限默认是按钮类型
  if (row.type === 1) {
    permissionForm.type = 2
  } else if (row.type === 2) {
    permissionForm.type = 3
  }
  dialogVisible.value = true
}

// 编辑权限
const handleEdit = (row) => {
  currentPermission.value = row
  Object.assign(permissionForm, {
    parent_id: row.parent_id,
    name: row.name,
    code: row.code,
    type: row.type,
    path: row.path,
    component: row.component,
    route_name: row.route_name,
    icon: row.icon,
    method: row.method,
    sort: row.sort,
    status: row.status,
    is_visible: row.is_visible !== false,
    is_keep_alive: row.is_keep_alive || false,
    is_external: row.is_external || false,
    description: row.description
  })
  dialogVisible.value = true
}

// 保存权限
const savePermission = async () => {
  if (!permissionFormRef.value) return

  await permissionFormRef.value.validate(async (valid) => {
    if (!valid) return

    saveLoading.value = true
    try {
      // 这里调用API保存权限
      ElMessage.success(currentPermission.value ? '权限更新成功' : '权限创建成功')
      dialogVisible.value = false
      getPermissionTree()
    } catch (error) {
      ElMessage.error(error.message || '保存失败')
    } finally {
      saveLoading.value = false
    }
  })
}

// 删除权限
const handleDelete = async (row) => {
  try {
    if (row.is_system) {
      ElMessage.error('系统内置权限无法删除')
      return
    }
    if (row.children && row.children.length > 0) {
      ElMessage.error('该权限下有子权限，无法删除')
      return
    }

    await ElMessageBox.confirm(
      `确定要删除权限 "${row.name}" 吗？删除后无法恢复`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 这里调用API删除权限
    ElMessage.success('权限删除成功')
    getPermissionTree()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 同步路由权限
const handleGenerate = () => {
  ElMessageBox.confirm(
    '确定要同步路由权限吗？系统会自动扫描路由文件生成权限配置',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    ElMessage.success('同步成功，新增权限已添加到系统中')
    getPermissionTree()
  }).catch(() => {})
}

onMounted(() => {
  getPermissionTree()
})
</script>

<style lang="scss" scoped>
.permission-manage-container {
}
</style>
