<template>
  <div class="layout-container">
    <el-container style="height: 100%">
      <!-- 侧边栏 -->
      <el-aside width="240px" class="sidebar-container">
        <el-menu
          :default-active="$route.path"
          router
          class="sidebar-menu"
          :collapse="isCollapse"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409eff"
        >
          <div class="logo-container" @click="toggleCollapse">
            <h1 v-if="!isCollapse" class="logo-title">电话营销系统</h1>
            <span v-else class="logo-icon">CC</span>
          </div>
          <template v-for="(item, index) in menuList" :key="index">
            <!-- 一级菜单有子菜单 -->
            <el-sub-menu v-if="item.children && item.children.length > 0" :index="item.path">
              <template #title>
                <el-icon><component :is="item.meta.icon" /></el-icon>
                <span>{{ item.meta.title }}</span>
              </template>
              <el-menu-item
                v-for="(child, childIndex) in item.children"
                :key="childIndex"
                :index="child.path"
                v-if="!child.meta.hideMenu && (!child.meta.isSuper || isSuperUser)"
              >
                <el-icon v-if="child.meta.icon"><component :is="child.meta.icon" /></el-icon>
                <span>{{ child.meta.title }}</span>
              </el-menu-item>
            </el-sub-menu>
            <!-- 一级菜单没有子菜单 -->
            <el-menu-item
              v-else
              :index="item.path"
              v-if="!item.meta.hideMenu && (!item.meta.isSuper || isSuperUser)"
            >
              <el-icon><component :is="item.meta.icon" /></el-icon>
              <template #title>{{ item.meta.title }}</template>
            </el-menu-item>
          </template>
        </el-menu>
      </el-aside>
      <el-container class="main-container">
        <!-- 顶部导航栏 -->
        <el-header class="header-container">
          <div class="header-left">
            <el-icon class="collapse-icon" @click="toggleCollapse">
              <Fold v-if="!isCollapse" />
              <Expand v-else />
            </el-icon>
            <el-breadcrumb separator="/">
              <el-breadcrumb-item
                v-for="(item, index) in breadcrumbList"
                :key="index"
                :to="{ path: item.path }"
              >
                {{ item.title }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="header-right">
            <el-tooltip content="刷新" placement="bottom">
              <el-icon class="header-icon" @click="refreshPage">
                <RefreshRight />
              </el-icon>
            </el-tooltip>
            <el-tooltip content="全屏" placement="bottom">
              <el-icon class="header-icon" @click="toggleFullscreen">
                <FullScreen v-if="!isFullscreen" />
                <Aim v-else />
              </el-icon>
            </el-tooltip>
            <el-dropdown trigger="hover">
              <div class="user-info">
                <el-avatar :size="32" :src="userStore.avatar">
                  {{ userStore.nickname?.charAt(0) || userStore.username.charAt(0) }}
                </el-avatar>
                <span class="username">{{ userStore.nickname || userStore.username }}</span>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="goProfile">
                    <el-icon><User /></el-icon>
                    个人中心
                  </el-dropdown-item>
                  <el-dropdown-item @click="goSettings">
                    <el-icon><Setting /></el-icon>
                    系统设置
                  </el-dropdown-item>
                  <el-dropdown-item @click="resetPassword">
                    <el-icon><Lock /></el-icon>
                    修改密码
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        <!-- 内容区域 -->
        <el-main class="content-container">
          <router-view v-slot="{ Component }">
            <transition name="fade-transform" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const isCollapse = ref(false)
const isFullscreen = ref(false)
const isSuperUser = computed(() => userStore.isSuperUser)
// 菜单列表
const menuList = computed(() => {
  const routes = router.options.routes.find(r => r.path === '/')?.children || []
  return routes.filter(r => !r.meta?.hideMenu)
})
// 面包屑
const breadcrumbList = computed(() => {
  const matched = route.matched.filter(r => r.meta?.title)
  return matched.map(r => ({
    path: r.path,
    title: r.meta.title
  }))
})
// 折叠侧边栏
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}
// 刷新页面
const refreshPage = () => {
  window.location.reload()
}
// 切换全屏
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    isFullscreen.value = true
  } else {
    document.exitFullscreen()
    isFullscreen.value = false
  }
}
// 跳转到个人中心
const goProfile = () => {
  router.push('/profile')
}
// 跳转到系统设置
const goSettings = () => {
  router.push('/settings')
}
// 修改密码
const resetPassword = () => {
  // TODO: 打开修改密码弹窗
  ElMessage.info('修改密码功能开发中')
}
// 退出登录
const handleLogout = () => {
  ElMessageBox.confirm(
    '确定要退出登录吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await userStore.logout()
      ElMessage.success('退出成功')
      router.push('/login')
    } catch (error) {
      ElMessage.error('退出失败，请重试')
    }
  })
}
onMounted(() => {
  // 监听全屏变化
  document.addEventListener('fullscreenchange', () => {
    isFullscreen.value = !!document.fullscreenElement
  })
})
</script>
<style lang="scss" scoped>
.layout-container {
  width: 100%;
  height: 100%;
}
.sidebar-container {
  background: #304156;
  height: 100%;
  overflow-y: auto;
  .sidebar-menu {
    border: none;
    height: 100%;
  }
  .logo-container {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #2b2f3a;
    cursor: pointer;
    .logo-title {
      color: #fff;
      font-size: 18px;
      font-weight: bold;
    }
    .logo-icon {
      color: #fff;
      font-size: 24px;
      font-weight: bold;
    }
  }
  :deep(.el-sub-menu__title) {
    &:hover {
      background-color: #263445 !important;
    }
  }
  :deep(.el-menu-item) {
    &:hover {
      background-color: #263445 !important;
    }
    &.is-active {
      background-color: #409eff !important;
      color: #fff !important;
    }
  }
}
.main-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}
.header-container {
  background: #fff;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  height: 60px;
  .header-left {
    display: flex;
    align-items: center;
    .collapse-icon {
      font-size: 20px;
      margin-right: 20px;
      cursor: pointer;
      color: #303133;
    }
  }
  .header-right {
    display: flex;
    align-items: center;
    .header-icon {
      font-size: 20px;
      margin-right: 20px;
      cursor: pointer;
      color: #666;
      &:hover {
        color: #409eff;
      }
    }
    .user-info {
      display: flex;
      align-items: center;
      cursor: pointer;
      .username {
        margin-left: 10px;
        color: #303133;
      }
      &:hover {
        .username {
          color: #409eff;
        }
      }
    }
  }
}
.content-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #f5f7fa;
}
.fade-transform-leave-active,
.fade-transform-enter-active {
  transition: all 0.3s ease;
}
.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}
.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
