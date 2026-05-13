import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/modules/user'
import websocketService from '@/utils/websocket'
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', requireAuth: false }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layout/index.vue'),
    redirect: '/dashboard',
    meta: { requireAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '首页', icon: 'Odometer' }
      },
      // 客户管理
      {
        path: 'customer',
        name: 'Customer',
        component: () => import('@/views/customer/index.vue'),
        meta: { title: '客户管理', icon: 'User' }
      },
      {
        path: 'customer/:id',
        name: 'CustomerDetail',
        component: () => import('@/views/customer/detail.vue'),
        meta: { title: '客户详情', hideMenu: true }
      },
      // 呼叫中心
      {
        path: 'call',
        name: 'Call',
        component: () => import('@/views/call/index.vue'),
        meta: { title: '呼叫中心', icon: 'Phone' }
      },
      {
        path: 'call/record',
        name: 'CallRecord',
        component: () => import('@/views/call/call-record.vue'),
        meta: { title: '通话记录', icon: 'Document' }
      },
      {
        path: 'call/task',
        name: 'CallTask',
        component: () => import('@/views/call/call-task.vue'),
        meta: { title: '呼叫任务', icon: 'List' }
      },
      {
        path: 'call/script',
        name: 'CallScript',
        component: () => import('@/views/call/script.vue'),
        meta: { title: '话术管理', icon: 'ChatDotRound' }
      },
      // 统计报表
      {
        path: 'report',
        name: 'Report',
        component: () => import('@/views/report/index.vue'),
        meta: { title: '统计报表', icon: 'DataAnalysis' }
      },
      {
        path: 'report/call-trend',
        name: 'CallTrendReport',
        component: () => import('@/views/report/call-trend.vue'),
        meta: { title: '通话趋势', icon: 'TrendCharts' }
      },
      {
        path: 'report/agent-performance',
        name: 'AgentPerformanceReport',
        component: () => import('@/views/report/agent-performance.vue'),
        meta: { title: '坐席绩效', icon: 'UserFilled' }
      },
      {
        path: 'report/customer-analysis',
        name: 'CustomerAnalysisReport',
        component: () => import('@/views/report/customer-analysis.vue'),
        meta: { title: '客户分析', icon: 'User' }
      },
      // 系统管理
      {
        path: 'system',
        name: 'System',
        component: () => import('@/views/system/index.vue'),
        meta: { title: '系统管理', icon: 'Setting', isSuper: true }
      },
      {
        path: 'system/user',
        name: 'UserManage',
        component: () => import('@/views/system/user.vue'),
        meta: { title: '用户管理', icon: 'User', isSuper: true }
      },
      {
        path: 'system/role',
        name: 'RoleManage',
        component: () => import('@/views/system/role.vue'),
        meta: { title: '角色管理', icon: 'Avatar', isSuper: true }
      },
      {
        path: 'system/permission',
        name: 'PermissionManage',
        component: () => import('@/views/system/permission.vue'),
        meta: { title: '权限管理', icon: 'Key', isSuper: true }
      },
      {
        path: 'system/config',
        name: 'SystemConfig',
        component: () => import('@/views/system/config.vue'),
        meta: { title: '系统配置', icon: 'Tools', isSuper: true }
      },
      {
        path: 'system/logs',
        name: 'OperationLogs',
        component: () => import('@/views/system/logs.vue'),
        meta: { title: '操作日志', icon: 'Document', isSuper: true }
      },
      // 个人中心
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/profile/index.vue'),
        meta: { title: '个人中心', hideMenu: true }
      },
      // 系统设置
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/settings/index.vue'),
        meta: { title: '系统设置', hideMenu: false, icon: 'Setting' }
      }
    ]
  },
  {
    path: '/404',
    name: '404',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '页面不存在', requireAuth: false }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404'
  }
]
const router = createRouter({
  history: createWebHistory(),
  routes
})
// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  const token = userStore.token
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 电话营销系统`
  }
  // 需要登录的路由
  if (to.meta.requireAuth !== false) {
    if (!token) {
      next({ path: '/login', query: { redirect: to.fullPath } })
      return
    }
    // 超级管理员权限验证
    if (to.meta.isSuper && !userStore.userInfo.is_superuser) {
      ElMessage.error('无权限访问')
      next(from.fullPath)
      return
    }
    // 连接WebSocket
    websocketService.connect()
  }
  // 已登录用户访问登录页跳转到首页
  if (to.path === '/login' && token) {
    next('/')
    return
  }
  next()
})
export default router
