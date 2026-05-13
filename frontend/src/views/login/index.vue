<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-title">
        <h2>电话营销系统</h2>
        <p>高效智能的客户联络解决方案</p>
      </div>
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-width="0"
        class="login-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
          >
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            @keyup.enter="handleLogin"
          >
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="login-footer">
        <p>© 2024 电话营销系统 版权所有</p>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const loginFormRef = ref(null)
const loginForm = reactive({
  username: '',
  password: ''
})

// 判断是否运行在Electron环境
const isElectron = window.electronAPI !== undefined
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3到20个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在6到20个字符之间', trigger: 'blur' }
  ]
}

onMounted(() => {
  // 监听Electron自动登录事件
  if (isElectron) {
    window.electronAPI.onAutoLogin(async (data) => {
      try {
        // 设置token和用户信息
        userStore.setToken(data.token)
        userStore.setUserInfo(data.userInfo)

        ElMessage.success('自动登录成功')
        const redirect = router.currentRoute.value.query?.redirect || '/'
        router.push(redirect)
      } catch (error) {
        console.error('自动登录失败:', error)
        // 清除无效的登录信息
        await window.electronAPI.clearLoginInfo()
      }
    })
  }
})

onUnmounted(() => {
  // 移除事件监听
  if (isElectron) {
    window.electronAPI.removeAllListeners('auto-login')
  }
})
const handleLogin = async () => {
  if (!loginFormRef.value) return
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const res = await userStore.login(loginForm)
        ElMessage.success('登录成功')

        // 如果是Electron环境，保存登录信息
        if (isElectron) {
          await window.electronAPI.saveLoginInfo({
            token: userStore.token,
            userInfo: userStore.userInfo
          })
        }

        const redirect = router.currentRoute.value.query?.redirect || '/'
        router.push(redirect)
      } catch (error) {
        ElMessage.error(error.message || '登录失败，请重试')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>
<style lang="scss" scoped>
.login-container {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}
.login-box {
  width: 480px;
  padding: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}
.login-title {
  text-align: center;
  margin-bottom: 40px;
  h2 {
    color: #303133;
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 10px;
  }
  p {
    color: #909399;
    font-size: 14px;
  }
}
.login-form {
  .login-btn {
    width: 100%;
    height: 48px;
    font-size: 16px;
  }
}
.login-footer {
  margin-top: 30px;
  text-align: center;
  color: #909399;
  font-size: 12px;
}
</style>
