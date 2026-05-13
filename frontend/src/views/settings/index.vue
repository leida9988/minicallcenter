<template>
  <div class="settings-container">
    <div class="common-card">
      <div class="card-header">
        <h3>系统设置</h3>
      </div>
      <el-form :model="settingsForm" label-width="150px">
        <el-divider content-position="left">通知设置</el-divider>
        <el-form-item label="来电通知">
          <el-switch v-model="settingsForm.notification.call" />
          <span class="ml-2 text-gray-500">有来电时显示系统通知</span>
        </el-form-item>
        <el-form-item label="消息通知">
          <el-switch v-model="settingsForm.notification.message" />
          <span class="ml-2 text-gray-500">有新消息时显示系统通知</span>
        </el-form-item>

        <el-divider content-position="left">通话设置</el-divider>
        <el-form-item label="自动接听">
          <el-switch v-model="settingsForm.autoAnswer" />
          <span class="ml-2 text-gray-500">来电时自动接听（仅在空闲状态下）</span>
        </el-form-item>
        <el-form-item label="通话弹窗">
          <el-switch v-model="settingsForm.autoPopup" />
          <span class="ml-2 text-gray-500">通话时自动弹出客户信息页面</span>
        </el-form-item>

        <el-divider content-position="left">快捷键设置</el-divider>
        <el-form-item label="接听电话">
          <el-input value="Ctrl+Alt+A" disabled style="width: 200px;" />
          <span class="ml-2 text-gray-500">全局快捷键，可在系统中直接接听电话</span>
        </el-form-item>
        <el-form-item label="挂断电话">
          <el-input value="Ctrl+Alt+S" disabled style="width: 200px;" />
          <span class="ml-2 text-gray-500">全局快捷键，可在系统中直接挂断电话</span>
        </el-form-item>
        <el-form-item label="显示/隐藏窗口">
          <el-input value="Ctrl+Alt+Z" disabled style="width: 200px;" />
          <span class="ml-2 text-gray-500">全局快捷键，可快速显示或隐藏窗口</span>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveSettings" :loading="saving">保存设置</el-button>
          <el-button @click="resetSettings">重置默认</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const saving = ref(false)
const isElectron = window.electronAPI !== undefined

const settingsForm = reactive({
  notification: {
    call: true,
    message: true
  },
  autoAnswer: false,
  autoPopup: true
})

const loadSettings = async () => {
  if (!isElectron) {
    ElMessage.info('当前环境不支持设置功能，请使用桌面客户端')
    return
  }

  try {
    const settings = await window.electronAPI.getSettings()
    Object.assign(settingsForm, settings)
  } catch (error) {
    ElMessage.error('加载设置失败')
  }
}

const saveSettings = async () => {
  if (!isElectron) {
    ElMessage.info('当前环境不支持设置功能，请使用桌面客户端')
    return
  }

  saving.value = true
  try {
    await window.electronAPI.saveSettings(settingsForm)
    ElMessage.success('设置保存成功')
  } catch (error) {
    ElMessage.error('保存设置失败')
  } finally {
    saving.value = false
  }
}

const resetSettings = () => {
  Object.assign(settingsForm, {
    notification: {
      call: true,
      message: true
    },
    autoAnswer: false,
    autoPopup: true
  })
  ElMessage.success('已重置为默认设置')
}

onMounted(() => {
  loadSettings()
})
</script>

<style lang="scss" scoped>
.settings-container {
  .card-header {
    margin-bottom: 20px;

    h3 {
      margin: 0;
      font-size: 18px;
      font-weight: bold;
    }
  }
}
</style>
