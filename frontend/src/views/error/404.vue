<template>
  <div class="error-page">
    <div class="error-content">
      <img src="@/assets/404.svg" alt="404" class="error-img">
      <h1>404</h1>
      <p>抱歉，您访问的页面不存在</p>
      <el-button type="primary" @click="goHome">返回首页</el-button>
    </div>
  </div>
</template>
<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
const goHome = () => {
  router.push('/')
}
</script>
<style lang="scss" scoped>
.error-page {
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  .error-content {
    text-align: center;
    .error-img {
      width: 400px;
      margin-bottom: 30px;
    }
    h1 {
      font-size: 120px;
      color: #409eff;
      line-height: 1.2;
      margin-bottom: 20px;
      text-shadow: 5px 5px 0 rgba(0, 0, 0, 0.1);
    }
    p {
      color: #909399;
      font-size: 18px;
      margin-bottom: 30px;
    }
  }
}
</style>
