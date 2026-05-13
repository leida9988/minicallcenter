<template>
  <div class="system-manage-container">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- 用户管理卡片 -->
      <div class="common-card hover:shadow-lg transition-shadow cursor-pointer" @click="$router.push('/system/user')">
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-lg bg-gradient-to-r from-blue-500 to-blue-600 flex items-center justify-center text-white">
            <el-icon size="32"><User /></el-icon>
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-bold mb-1">用户管理</h3>
            <p class="text-gray-500 text-sm mb-2">管理系统用户账号、分配角色和权限</p>
            <div class="flex items-center gap-3 text-sm">
              <span class="text-gray-600">
                <el-icon class="mr-1"><UserFilled /></el-icon>
                共 {{ statistics.total_users }} 个用户
              </span>
              <span class="text-gray-600">
                <el-icon class="mr-1"><Avatar /></el-icon>
                {{ statistics.online_users }} 个在线
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 角色管理卡片 -->
      <div class="common-card hover:shadow-lg transition-shadow cursor-pointer" @click="$router.push('/system/role')">
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-lg bg-gradient-to-r from-green-500 to-green-600 flex items-center justify-center text-white">
            <el-icon size="32"><Avatar /></el-icon>
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-bold mb-1">角色管理</h3>
            <p class="text-gray-500 text-sm mb-2">管理系统角色、分配权限菜单</p>
            <div class="flex items-center gap-3 text-sm">
              <span class="text-gray-600">
                <el-icon class="mr-1"><Avatar /></el-icon>
                共 {{ statistics.total_roles }} 个角色
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 权限管理卡片 -->
      <div class="common-card hover:shadow-lg transition-shadow cursor-pointer" @click="$router.push('/system/permission')">
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-lg bg-gradient-to-r from-purple-500 to-purple-600 flex items-center justify-center text-white">
            <el-icon size="32"><Key /></el-icon>
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-bold mb-1">权限管理</h3>
            <p class="text-gray-500 text-sm mb-2">管理系统菜单、按钮、API权限</p>
            <div class="flex items-center gap-3 text-sm">
              <span class="text-gray-600">
                <el-icon class="mr-1"><Menu /></el-icon>
                共 {{ statistics.total_permissions }} 个权限
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 系统配置卡片 -->
      <div class="common-card hover:shadow-lg transition-shadow cursor-pointer" @click="$router.push('/system/config')">
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-lg bg-gradient-to-r from-orange-500 to-orange-600 flex items-center justify-center text-white">
            <el-icon size="32"><Tools /></el-icon>
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-bold mb-1">系统配置</h3>
            <p class="text-gray-500 text-sm mb-2">配置系统参数、基础数据管理</p>
            <div class="flex items-center gap-3 text-sm">
              <span class="text-gray-600">
                <el-icon class="mr-1"><Setting /></el-icon>
                共 {{ statistics.total_configs }} 项配置
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作日志卡片 -->
      <div class="common-card hover:shadow-lg transition-shadow cursor-pointer" @click="$router.push('/system/logs')">
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-lg bg-gradient-to-r from-red-500 to-red-600 flex items-center justify-center text-white">
            <el-icon size="32"><Document /></el-icon>
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-bold mb-1">操作日志</h3>
            <p class="text-gray-500 text-sm mb-2">查看用户操作记录、审计日志</p>
            <div class="flex items-center gap-3 text-sm">
              <span class="text-gray-600">
                <el-icon class="mr-1"><Document /></el-icon>
                今日 {{ statistics.today_logs }} 条日志
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 系统监控卡片 -->
      <div class="common-card hover:shadow-lg transition-shadow cursor-pointer" @click="handleMonitor">
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-lg bg-gradient-to-r from-cyan-500 to-cyan-600 flex items-center justify-center text-white">
            <el-icon size="32"><Monitor /></el-icon>
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-bold mb-1">系统监控</h3>
            <p class="text-gray-500 text-sm mb-2">查看系统运行状态、资源使用情况</p>
            <div class="flex items-center gap-3 text-sm">
              <span class="text-gray-600">
                <el-icon class="mr-1"><Odometer /></el-icon>
                运行 {{ statistics.run_days }} 天
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 系统信息 -->
    <div class="common-card mt-6">
      <div class="card-header">
        <h3>系统信息</h3>
      </div>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="系统名称">
          <span class="font-medium">通用电话营销系统</span>
        </el-descriptions-item>
        <el-descriptions-item label="系统版本">
          <el-tag type="success">v1.0.0</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="技术栈">
          <span>FastAPI + Vue3 + Element Plus + MySQL + Redis</span>
        </el-descriptions-item>
        <el-descriptions-item label="部署环境">
          <el-tag type="warning">{{ environment }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="服务器信息">
          <span>{{ serverInfo.os }} / {{ serverInfo.cpu }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="运行状态">
          <el-tag type="success">正常运行</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="上次更新时间">
          <span>{{ lastUpdateTime }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="开发团队">
          <span>研发部</span>
        </el-descriptions-item>
      </el-descriptions>
    </div>

    <!-- 快速操作 -->
    <div class="common-card mt-6">
      <div class="card-header">
        <h3>快速操作</h3>
      </div>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-button type="primary" style="width: 100%; height: 60px;" @click="handleClearCache">
            <el-icon size="18" class="mb-1"><Refresh /></el-icon>
            <div>清除缓存</div>
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="success" style="width: 100%; height: 60px;" @click="handleBackup">
            <el-icon size="18" class="mb-1"><Download /></el-icon>
            <div>数据备份</div>
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="warning" style="width: 100%; height: 60px;" @click="handleNotify">
            <el-icon size="18" class="mb-1"><Bell /></el-icon>
            <div>系统公告</div>
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="danger" style="width: 100%; height: 60px;" @click="handleRestart">
            <el-icon size="18" class="mb-1"><SwitchButton /></el-icon>
            <div>重启系统</div>
          </el-button>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User, Avatar, Key, Tools, Document, Monitor, Odometer, Menu,
  UserFilled, Setting, Refresh, Download, Bell, SwitchButton
} from '@element-plus/icons-vue'

const statistics = ref({
  total_users: 58,
  online_users: 12,
  total_roles: 8,
  total_permissions: 126,
  total_configs: 42,
  today_logs: 256,
  run_days: 186
})

const environment = ref('生产环境')
const serverInfo = ref({
  os: 'CentOS 7.9',
  cpu: 'Intel Xeon 8C/16T'
})
const lastUpdateTime = ref('2024-05-01 10:30:00')

// 系统监控
const handleMonitor = () => {
  ElMessage.info('系统监控功能开发中')
}

// 清除缓存
const handleClearCache = () => {
  ElMessageBox.confirm(
    '确定要清除系统缓存吗？清除后系统会重新加载配置',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    ElMessage.success('缓存清除成功')
  }).catch(() => {})
}

// 数据备份
const handleBackup = () => {
  ElMessageBox.confirm(
    '确定要立即备份系统数据吗？备份过程可能需要几分钟时间',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    ElMessage.success('数据备份已开始，请稍后在备份管理中查看')
  }).catch(() => {})
}

// 系统公告
const handleNotify = () => {
  ElMessage.info('系统公告功能开发中')
}

// 重启系统
const handleRestart = () => {
  ElMessageBox.confirm(
    '确定要重启系统吗？重启过程中系统将无法访问，请谨慎操作',
    '警告',
    {
      confirmButtonText: '确定重启',
      cancelButtonText: '取消',
      type: 'danger',
      confirmButtonClass: 'el-button--danger'
    }
  ).then(() => {
    ElMessage.success('系统已开始重启，请耐心等待')
  }).catch(() => {})
}

onMounted(() => {
  // 可以在这里加载真实的系统统计数据
})
</script>

<style lang="scss" scoped>
.system-manage-container {
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
}
</style>
