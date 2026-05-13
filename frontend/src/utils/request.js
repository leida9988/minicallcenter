import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/modules/user'
import router from '@/router'
// 创建axios实例
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000
})
// 请求拦截
service.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers['Authorization'] = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)
// 响应拦截
service.interceptors.response.use(
  (response) => {
    const res = response.data
    // 下载文件直接返回
    if (response.config.responseType === 'blob') {
      return res
    }
    // 正常响应
    if (res.code === 200 || res.code === 0) {
      return res
    }
    // 错误处理
    ElMessage.error(res.message || '请求失败')
    return Promise.reject(new Error(res.message || '请求失败'))
  },
  (error) => {
    console.error('Response error:', error)
    const userStore = useUserStore()
    const { response } = error
    if (response) {
      switch (response.status) {
        case 401:
          ElMessageBox.confirm(
            '登录状态已过期，请重新登录',
            '系统提示',
            {
              confirmButtonText: '重新登录',
              cancelButtonText: '取消',
              type: 'warning'
            }
          ).then(() => {
            userStore.resetToken()
            router.push({ path: '/login', query: { redirect: router.currentRoute.value.fullPath } })
          })
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(response.data.message || `请求错误：${response.status}`)
      }
    } else {
      ElMessage.error('网络连接异常，请稍后重试')
    }
    return Promise.reject(error)
  }
)
export default service
