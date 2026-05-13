import { defineStore } from 'pinia'
import { loginApi, logoutApi, getUserInfoApi } from '@/api/user'
import { setToken, getToken, removeToken } from '@/utils/auth'
export const useUserStore = defineStore('user', {
  state: () => ({
    token: getToken() || '',
    userInfo: {},
    permissions: []
  }),
  getters: {
    isSuperUser: (state) => state.userInfo.is_superuser || false,
    username: (state) => state.userInfo.username || '',
    nickname: (state) => state.userInfo.nickname || '',
    avatar: (state) => state.userInfo.avatar || ''
  },
  actions: {
    // 登录
    async login(loginForm) {
      try {
        const res = await loginApi(loginForm)
        const { access_token, user } = res.data
        this.token = access_token
        this.userInfo = user
        setToken(access_token)
        return Promise.resolve(res)
      } catch (error) {
        return Promise.reject(error)
      }
    },
    // 获取用户信息
    async getUserInfo() {
      try {
        const res = await getUserInfoApi()
        const { user, permissions } = res.data
        this.userInfo = user
        this.permissions = permissions
        return Promise.resolve(res)
      } catch (error) {
        return Promise.reject(error)
      }
    },
    // 登出
    async logout() {
      try {
        await logoutApi()
        this.token = ''
        this.userInfo = {}
        this.permissions = []
        removeToken()
        return Promise.resolve()
      } catch (error) {
        return Promise.reject(error)
      }
    },
    // 重置token
    resetToken() {
      this.token = ''
      this.userInfo = {}
      this.permissions = []
      removeToken()
    }
  },
  persist: {
    key: 'user-store',
    storage: localStorage,
    paths: ['token', 'userInfo']
  }
})
