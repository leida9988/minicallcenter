<template>
  <div class="call-container">
    <el-row :gutter="20">
      <!-- 左侧拨号面板 -->
      <el-col :span="8">
        <div class="common-card">
          <div class="agent-status">
            <span class="status-label">坐席状态：</span>
            <el-select v-model="currentStatus" @change="handleStatusChange" style="width: 120px">
              <el-option label="空闲" :value="1" style="color: #67c23a" />
              <el-option label="忙碌" :value="2" style="color: #e6a23c" />
              <el-option label="小憩" :value="3" style="color: #f56c6c" />
              <el-option label="离线" :value="4" style="color: #909399" />
            </el-select>
          </div>

          <!-- 拨号盘 -->
          <div class="dial-pad">
            <el-input v-model="dialNumber" placeholder="请输入电话号码" class="dial-input" @keyup.enter="handleCall">
              <template #append>
                <el-button :type="callStatus === 'idle' ? 'primary' : 'danger'" @click="callStatus === 'idle' ? handleCall() : handleHangup()">
                  <el-icon><Phone /></el-icon>
                  {{ callStatus === 'idle' ? '拨打' : '挂断' }}
                </el-button>
              </template>
            </el-input>

            <div class="dial-buttons">
              <el-button v-for="num in 9" :key="num" class="dial-btn" @click="appendNumber(num.toString())">
                {{ num }}
              </el-button>
              <el-button class="dial-btn" @click="appendNumber('*')">*</el-button>
              <el-button class="dial-btn" @click="appendNumber('0')">0</el-button>
              <el-button class="dial-btn" @click="appendNumber('#')">#</el-button>
              <el-button class="dial-btn dial-btn-clear" @click="clearNumber">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>

          <!-- 通话控制按钮 -->
          <div class="call-controls" v-if="callStatus !== 'idle'">
            <el-button :type="isMuted ? 'danger' : 'primary'" @click="toggleMute" circle>
              <el-icon><Microphone /></el-icon>
            </el-button>
            <el-button :type="isHeld ? 'danger' : 'primary'" @click="toggleHold" circle>
              <el-icon><PauseOutline /></el-icon>
            </el-button>
            <el-button type="primary" @click="handleTransfer" circle>
              <el-icon><SwitchButton /></el-icon>
            </el-button>
            <el-button type="primary" @click="handleThreeWay" circle>
              <el-icon><UserPlus /></el-icon>
            </el-button>
            <el-button type="success" @click="showRecordForm = true" circle>
              <el-icon><Document /></el-icon>
            </el-button>
          </div>

          <!-- 通话时长 -->
          <div class="call-duration" v-if="callStatus === 'connected'">
            <el-icon><Timer /></el-icon>
            <span>{{ formatDuration(callDuration) }}</span>
          </div>
        </div>

        <!-- 快速呼叫列表 -->
        <div class="common-card mt-20">
          <div class="card-header">
            <h3>快速呼叫</h3>
            <el-button type="text" @click="refreshQuickCalls">刷新</el-button>
          </div>
          <div class="quick-call-list">
            <div
              v-for="item in quickCallList"
              :key="item.id"
              class="quick-call-item"
              @click="quickCall(item)"
            >
              <div class="customer-name">{{ item.name }}</div>
              <div class="customer-phone">{{ item.phone }}</div>
              <el-button type="primary" text size="small">拨打</el-button>
            </div>
            <div v-if="quickCallList.length === 0" class="empty-tip">
              暂无快速呼叫联系人
            </div>
          </div>
        </div>
      </el-col>

      <!-- 右侧客户信息和跟进记录 -->
      <el-col :span="16">
        <!-- 客户信息卡片 -->
        <div class="common-card" v-if="currentCustomer">
          <div class="customer-header">
            <el-avatar :size="60" class="customer-avatar">
              {{ currentCustomer.name?.charAt(0) || '客' }}
            </el-avatar>
            <div class="customer-info">
              <div class="customer-name">
                {{ currentCustomer.name }}
                <el-tag :type="getLevelTagType(currentCustomer.level)" size="small" class="ml-2">
                  {{ getLevelText(currentCustomer.level) }}
                </el-tag>
                <el-tag :type="getStatusTagType(currentCustomer.status)" size="small" class="ml-2">
                  {{ getStatusText(currentCustomer.status) }}
                </el-tag>
              </div>
              <div class="customer-contact">
                <span class="contact-item">
                  <el-icon><Phone /></el-icon>
                  {{ currentCustomer.phone }}
                </span>
                <span class="contact-item" v-if="currentCustomer.company">
                  <el-icon><OfficeBuilding /></el-icon>
                  {{ currentCustomer.company }}
                </span>
              </div>
            </div>
          </div>

          <el-descriptions :column="3" border class="mt-20">
            <el-descriptions-item label="性别">
              {{ getGenderText(currentCustomer.gender) }}
            </el-descriptions-item>
            <el-descriptions-item label="年龄">
              {{ currentCustomer.age || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="电子邮箱">
              {{ currentCustomer.email || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="职位">
              {{ currentCustomer.position || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="客户来源">
              {{ currentCustomer.source || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="所属坐席">
              {{ currentCustomer.assign_user_name || '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 空状态 -->
        <div class="common-card empty-card" v-else>
          <el-empty description="请输入号码拨打或等待来电" />
        </div>

        <!-- 历史跟进记录 -->
        <div class="common-card mt-20" v-if="currentCustomer">
          <div class="card-header">
            <h3>历史跟进记录</h3>
            <el-button type="primary" text @click="goToCustomerDetail">查看全部</el-button>
          </div>
          <div class="follow-timeline">
            <el-timeline v-loading="followLoading">
              <el-timeline-item
                v-for="item in recentFollows"
                :key="item.id"
                :timestamp="item.follow_time"
                placement="top"
              >
                <template #dot>
                  <el-icon :color="getTypeColor(item.type)" size="18">
                    <component :is="getTypeIcon(item.type)" />
                  </el-icon>
                </template>
                <el-card shadow="hover" size="small">
                  <div class="follow-header">
                    <span class="follow-type">{{ getTypeText(item.type) }}</span>
                    <span class="follow-duration" v-if="item.duration">
                      通话时长：{{ formatDuration(item.duration) }}
                    </span>
                  </div>
                  <div class="follow-content">
                    <p>{{ item.content }}</p>
                    <p v-if="item.result" class="follow-result">
                      <strong>结果：</strong>{{ item.result }}
                    </p>
                  </div>
                </el-card>
              </el-timeline-item>
              <div v-if="recentFollows.length === 0 && !followLoading" class="empty-tip">
                暂无跟进记录
              </div>
            </el-timeline>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 跟进记录表单对话框 -->
    <el-dialog
      v-model="showRecordForm"
      title="添加跟进记录"
      width="600px"
    >
      <el-form :model="followForm" label-width="80px">
        <el-form-item label="跟进类型">
          <el-select v-model="followForm.type" style="width: 100%">
            <el-option label="电话跟进" :value="1" />
            <el-option label="微信跟进" :value="2" />
            <el-option label="线下拜访" :value="3" />
            <el-option label="短信跟进" :value="4" />
            <el-option label="邮件跟进" :value="5" />
          </el-select>
        </el-form-item>
        <el-form-item label="跟进内容">
          <el-input
            v-model="followForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入跟进内容"
          />
        </el-form-item>
        <el-form-item label="跟进结果">
          <el-input
            v-model="followForm.result"
            type="textarea"
            :rows="2"
            placeholder="请输入跟进结果"
          />
        </el-form-item>
        <el-form-item label="下次跟进">
          <el-date-picker
            v-model="followForm.next_follow_time"
            type="datetime"
            placeholder="请选择下次跟进时间"
            style="width: 100%"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="通话时长">
          <el-input-number
            v-model="followForm.duration"
            :min="0"
            placeholder="秒"
            style="width: 120px"
          />
          <span class="ml-2">秒</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRecordForm = false">取消</el-button>
        <el-button type="primary" @click="saveFollowRecord" :loading="saveLoading">保存</el-button>
      </template>
    </el-dialog>

    <!-- 来电弹框 -->
    <el-dialog
      v-model="showIncomingDialog"
      title="来电提醒"
      width="400px"
      close-on-click-modal={false}
      close-on-press-escape={false}
      show-close={false}
    >
      <div class="incoming-call">
        <el-icon size="60" color="#409eff" class="mb-20">
          <Phone />
        </el-icon>
        <h3>有新的来电</h3>
        <p class="caller-number">{{ callerNumber }}</p>
        <p class="customer-name" v-if="currentCustomer">
          客户：{{ currentCustomer.name }}
        </p>
        <div class="incoming-actions">
          <el-button type="danger" size="large" @click="handleReject">拒接</el-button>
          <el-button type="success" size="large" @click="handleAnswer">接听</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, getCurrentInstance } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Phone, Delete, Microphone, PauseOutline, SwitchButton, UserPlus, Document, Timer, OfficeBuilding } from '@element-plus/icons-vue'
import { getCustomerDetailApi, createFollowRecordApi } from '@/api/customer'
import { updateAgentStatusApi } from '@/api/call'
import { formatDuration } from '@/utils/datetime'

const { proxy } = getCurrentInstance()
const router = useRouter()
const route = useRoute()
const websocket = proxy.$websocket
// 判断是否运行在Electron环境
const isElectron = window.electronAPI !== undefined
const currentStatus = ref(1)
const dialNumber = ref('')
const callStatus = ref('idle') // idle, calling, connected, disconnected, incoming
const callDuration = ref(0)
const isMuted = ref(false)
const isHeld = ref(false)
const currentCustomer = ref(null)
const currentCallId = ref(null)
const callerNumber = ref('')
const quickCallList = ref([])
const recentFollows = ref([])
const followLoading = ref(false)
const showRecordForm = ref(false)
const showIncomingDialog = ref(false)
const saveLoading = ref(false)
let durationTimer = null

// 跟进表单
const followForm = reactive({
  customer_id: null,
  type: 1,
  content: '',
  result: '',
  next_follow_time: '',
  duration: 0
})

// 追加号码
const appendNumber = (num) => {
  dialNumber.value += num
}

// 清空号码
const clearNumber = () => {
  dialNumber.value = ''
}

// 拨打电话
const handleCall = async () => {
  if (!dialNumber.value.trim()) {
    ElMessage.warning('请输入电话号码')
    return
  }

  const success = websocket.makeCall(dialNumber.value, currentCustomer.value?.id)
  if (success) {
    callStatus.value = 'calling'
    ElMessage.success('正在拨号...')
  } else {
    ElMessage.error('拨号失败，请检查WebSocket连接')
  }
}

// 挂断电话
const handleHangup = async () => {
  const success = websocket.hangupCall()
  if (success) {
    callStatus.value = 'disconnected'
    isMuted.value = false
    isHeld.value = false

    if (durationTimer) {
      clearInterval(durationTimer)
      durationTimer = null
    }

    ElMessage.success('通话已结束')

    // 自动弹出跟进记录表单
    if (currentCustomer.value) {
      followForm.customer_id = currentCustomer.value.id
      followForm.duration = callDuration.value
      showRecordForm.value = true
    }

    callDuration.value = 0
  } else {
    ElMessage.error('挂断失败，请检查WebSocket连接')
  }
}

// 切换静音
const toggleMute = async () => {
  // TODO: 实现静音功能通过WebSocket
  ElMessage.info('静音功能开发中')
}

// 切换保持
const toggleHold = async () => {
  if (isHeld.value) {
    const success = websocket.resumeCall()
    if (success) {
      isHeld.value = false
      ElMessage.success('已恢复通话')
    } else {
      ElMessage.error('恢复通话失败')
    }
  } else {
    const success = websocket.holdCall()
    if (success) {
      isHeld.value = true
      ElMessage.success('已保持通话')
    } else {
      ElMessage.error('保持通话失败')
    }
  }
}

// 通话转接
const handleTransfer = () => {
  // 弹框选择要转接的坐席
  ElMessage.info('转接功能开发中')
}

// 三方通话
const handleThreeWay = () => {
  ElMessage.info('三方通话功能开发中')
}

// 保存跟进记录
const saveFollowRecord = async () => {
  if (!followForm.content.trim()) {
    ElMessage.warning('请输入跟进内容')
    return
  }

  saveLoading.value = true
  try {
    await createFollowRecordApi(followForm)
    ElMessage.success('保存成功')
    showRecordForm.value = false

    // 重置表单
    followForm.content = ''
    followForm.result = ''
    followForm.next_follow_time = ''
    followForm.duration = 0

    // 刷新跟进记录列表
    if (currentCustomer.value) {
      loadRecentFollows(currentCustomer.value.id)
    }
  } catch (error) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    saveLoading.value = false
  }
}

// 加载客户信息
const loadCustomerInfo = async (customerId) => {
  try {
    const res = await getCustomerDetailApi(customerId)
    currentCustomer.value = res.data
    loadRecentFollows(customerId)
  } catch (error) {
    ElMessage.error('加载客户信息失败')
  }
}

// 加载最近跟进记录
const loadRecentFollows = async (customerId) => {
  followLoading.value = true
  try {
    // 这里暂时使用模拟数据，后续替换为真实API
    recentFollows.value = [
      {
        id: 1,
        type: 1,
        content: '客户表示对产品感兴趣，需要进一步了解价格详情',
        result: '已发送产品报价单',
        follow_time: '2024-05-12 14:30:00',
        duration: 185
      },
      {
        id: 2,
        type: 2,
        content: '微信沟通产品功能，客户询问是否支持定制',
        result: '已告知可以定制，需要提供具体需求',
        follow_time: '2024-05-10 10:15:00'
      }
    ]
  } catch (error) {
    ElMessage.error('加载跟进记录失败')
  } finally {
    followLoading.value = false
  }
}

// 快速呼叫
const quickCall = (item) => {
  dialNumber.value = item.phone
  handleCall()
}

// 刷新快速呼叫列表
const refreshQuickCalls = () => {
  // 模拟数据
  quickCallList.value = [
    { id: 1, name: '张三', phone: '13800138001' },
    { id: 2, name: '李四', phone: '13800138002' },
    { id: 3, name: '王五', phone: '13800138003' }
  ]
}

// 更改坐席状态
const handleStatusChange = async (status) => {
  try {
    await updateAgentStatusApi({ status })
    ElMessage.success('状态已更新')
  } catch (error) {
    ElMessage.error('状态更新失败')
    // 回滚状态
    currentStatus.value = status === 1 ? 2 : 1
  }
}

// 跳转到客户详情页
const goToCustomerDetail = () => {
  if (currentCustomer.value) {
    router.push(`/customer/${currentCustomer.value.id}`)
  }
}

// 获取等级标签类型
const getLevelTagType = (level) => {
  const typeMap = {
    1: 'info',
    2: 'warning',
    3: 'danger'
  }
  return typeMap[level] || 'info'
}

// 获取等级文本
const getLevelText = (level) => {
  const textMap = {
    1: '普通',
    2: 'VIP',
    3: '重要客户'
  }
  return textMap[level] || '未知'
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const typeMap = {
    1: 'info',
    2: 'primary',
    3: 'success',
    4: 'danger',
    5: 'warning',
    6: 'default'
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const textMap = {
    1: '待联系',
    2: '联系中',
    3: '有意向',
    4: '已成交',
    5: '已拒绝',
    6: '无效客户'
  }
  return textMap[status] || '未知'
}

// 获取性别文本
const getGenderText = (gender) => {
  const textMap = {
    0: '未知',
    1: '男',
    2: '女'
  }
  return textMap[gender] || '未知'
}

// 获取跟进类型图标
const getTypeIcon = (type) => {
  const iconMap = {
    1: 'Phone',
    2: 'ChatDotRound',
    3: 'Location',
    4: 'Message',
    5: 'Message'
  }
  return iconMap[type] || 'Document'
}

// 获取跟进类型颜色
const getTypeColor = (type) => {
  const colorMap = {
    1: '#409eff',
    2: '#67c23a',
    3: '#e6a23c',
    4: '#f56c6c',
    5: '#909399'
  }
  return colorMap[type] || '#909399'
}

// 获取跟进类型文本
const getTypeText = (type) => {
  const textMap = {
    1: '电话跟进',
    2: '微信跟进',
    3: '线下拜访',
    4: '短信跟进',
    5: '邮件跟进'
  }
  return textMap[type] || '其他跟进'
}

// 接听来电
const handleAnswer = () => {
  const success = websocket.answerCall()
  if (success) {
    showIncomingDialog.value = false
    callStatus.value = 'connected'
    ElMessage.success('已接听')
    // 开始计时
    durationTimer = setInterval(() => {
      callDuration.value += 1
    }, 1000)
  } else {
    ElMessage.error('接听失败')
  }
}

// 拒接来电
const handleReject = () => {
  const success = websocket.hangupCall()
  if (success) {
    showIncomingDialog.value = false
    callStatus.value = 'idle'
    ElMessage.success('已拒接')
  } else {
    ElMessage.error('拒接失败')
  }
}

onMounted(() => {
  refreshQuickCalls()

  // 处理路由参数，如果有电话号码则自动填充
  if (route.query.phone) {
    dialNumber.value = route.query.phone
    if (route.query.customer_id) {
      loadCustomerInfo(route.query.customer_id)
    }
  }

  // Electron环境下监听快捷键事件
  if (isElectron) {
    // 接听电话快捷键
    window.electronAPI.onShortcutAnswerCall(() => {
      if (callStatus.value === 'incoming') {
        handleAnswer()
      }
    })

    // 挂断电话快捷键
    window.electronAPI.onShortcutHangupCall(() => {
      if (callStatus.value === 'connected' || callStatus.value === 'incoming') {
        handleHangup()
      }
    })
  }

  // 监听WebSocket呼叫事件
  websocket.on('call_event', (data) => {
    switch (data.event) {
      case 'incoming_call':
        callStatus.value = 'incoming'
        callerNumber.value = data.caller_number
        currentCallId.value = data.call_id
        showIncomingDialog.value = true
        // 查询客户信息
        if (data.customer_id) {
          loadCustomerInfo(data.customer_id)
        }
        // Electron环境下显示系统通知
        if (isElectron) {
          window.electronAPI.showIncomingCallNotification({
            phoneNumber: data.caller_number,
            customerName: currentCustomer.value?.name || '未知客户'
          })
        }
        break
      case 'call_connected':
        callStatus.value = 'connected'
        currentCallId.value = data.call_id
        // 开始计时
        durationTimer = setInterval(() => {
          callDuration.value += 1
        }, 1000)
        break
      case 'call_disconnected':
        callStatus.value = 'disconnected'
        isMuted.value = false
        isHeld.value = false
        if (durationTimer) {
          clearInterval(durationTimer)
          durationTimer = null
        }
        // 自动弹出跟进记录表单
        if (currentCustomer.value) {
          followForm.customer_id = currentCustomer.value.id
          followForm.duration = callDuration.value
          showRecordForm.value = true
        }
        callDuration.value = 0
        break
      case 'call_failed':
        callStatus.value = 'idle'
        ElMessage.error(`呼叫失败：${data.reason || '未知错误'}`)
        break
    }
  })

  // 监听呼叫状态变化
  websocket.on('call_status', (data) => {
    if (data.call_id === currentCallId.value) {
      callStatus.value = data.status
      isMuted.value = data.is_muted
      isHeld.value = data.is_held
    }
  })
})

onUnmounted(() => {
  if (durationTimer) {
    clearInterval(durationTimer)
  }
  // 移除WebSocket事件监听
  websocket.off('call_event')
  websocket.off('call_status')

  // 移除Electron事件监听
  if (isElectron) {
    window.electronAPI.removeAllListeners('shortcut-answer-call')
    window.electronAPI.removeAllListeners('shortcut-hangup-call')
  }
})
</script>

<style lang="scss" scoped>
.call-container {
  .agent-status {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    .status-label {
      margin-right: 10px;
      font-weight: 500;
    }
  }

  .dial-pad {
    .dial-input {
      margin-bottom: 20px;
    }

    .dial-buttons {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;

      .dial-btn {
        height: 60px;
        font-size: 20px;
        font-weight: 500;
      }

      .dial-btn-clear {
        color: #f56c6c;
      }
    }
  }

  .call-controls {
    display: flex;
    justify-content: center;
    gap: 15px;
    margin: 20px 0;

    .el-button {
      width: 50px;
      height: 50px;
      font-size: 20px;
    }
  }

  .call-duration {
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    color: #409eff;

    .el-icon {
      margin-right: 10px;
    }
  }

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

  .quick-call-list {
    .quick-call-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 0;
      border-bottom: 1px solid #f0f0f0;
      cursor: pointer;

      &:last-child {
        border-bottom: none;
      }

      &:hover {
        background-color: #f5f7fa;
      }

      .customer-name {
        font-weight: 500;
        margin-bottom: 5px;
      }

      .customer-phone {
        color: #909399;
        font-size: 14px;
      }
    }

    .empty-tip {
      text-align: center;
      color: #909399;
      padding: 20px 0;
    }
  }

  .customer-header {
    display: flex;
    align-items: center;

    .customer-avatar {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #fff;
      font-size: 24px;
      font-weight: bold;
      margin-right: 20px;
    }

    .customer-info {
      flex: 1;

      .customer-name {
        font-size: 20px;
        font-weight: bold;
        color: #303133;
        margin-bottom: 10px;
      }

      .customer-contact {
        .contact-item {
          display: inline-flex;
          align-items: center;
          color: #606266;
          margin-right: 30px;

          .el-icon {
            margin-right: 5px;
            color: #909399;
          }
        }
      }
    }
  }

  .empty-card {
    min-height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .follow-timeline {
    padding-left: 10px;

    .follow-header {
      display: flex;
      align-items: center;
      margin-bottom: 8px;

      .follow-type {
        font-weight: bold;
        color: #409eff;
        margin-right: 20px;
      }

      .follow-duration {
        color: #909399;
        font-size: 12px;
      }
    }

    .follow-content {
      p {
        margin-bottom: 5px;
        color: #606266;
        font-size: 14px;
      }

      .follow-result {
        color: #67c23a;
      }
    }
  }

  .incoming-call {
    text-align: center;
    padding: 20px 0;

    .caller-number {
      font-size: 24px;
      font-weight: bold;
      color: #303133;
      margin: 20px 0;
    }

    .customer-name {
      font-size: 16px;
      color: #606266;
      margin-bottom: 30px;
    }

    .incoming-actions {
      display: flex;
      justify-content: center;
      gap: 20px;

      .el-button {
        width: 100px;
      }
    }
  }
}
</style>
