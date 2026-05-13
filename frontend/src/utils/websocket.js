import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/modules/user'

class WebSocketService {
  constructor() {
    this.socket = null
    this.url = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'
    this.heartbeatInterval = null
    this.reconnectTimeout = null
    this.reconnectCount = 0
    this.maxReconnectCount = 10
    this.eventListeners = new Map()
  }

  connect() {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      return
    }

    const userStore = useUserStore()
    const token = userStore.token

    if (!token) {
      console.error('WebSocket connection failed: No token available')
      return
    }

    try {
      this.socket = new WebSocket(`${this.url}?token=${token}`)

      this.socket.onopen = this.onOpen.bind(this)
      this.socket.onmessage = this.onMessage.bind(this)
      this.socket.onerror = this.onError.bind(this)
      this.socket.onclose = this.onClose.bind(this)
    } catch (error) {
      console.error('WebSocket connection error:', error)
      this.reconnect()
    }
  }

  onOpen() {
    console.log('WebSocket connected successfully')
    this.reconnectCount = 0
    this.startHeartbeat()
    this.emit('connected')
  }

  onMessage(event) {
    try {
      const data = JSON.parse(event.data)

      // 处理不同类型的消息
      switch (data.type) {
        case 'call_status':
          this.handleCallStatus(data.data)
          break
        case 'call_event':
          this.handleCallEvent(data.data)
          break
        case 'notification':
          this.handleNotification(data.data)
          break
        case 'heartbeat':
          // 心跳响应，无需处理
          break
        default:
          console.log('Unknown WebSocket message type:', data.type)
      }

      this.emit(data.type, data.data)
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error)
    }
  }

  onError(error) {
    console.error('WebSocket error:', error)
    this.emit('error', error)
  }

  onClose(event) {
    console.log('WebSocket disconnected:', event.code, event.reason)
    this.stopHeartbeat()
    this.emit('disconnected')

    // 自动重连，除非是主动关闭
    if (event.code !== 1000) {
      this.reconnect()
    }
  }

  reconnect() {
    if (this.reconnectCount >= this.maxReconnectCount) {
      console.error('WebSocket reconnect failed after maximum attempts')
      ElMessage.error('WebSocket连接失败，请刷新页面重试')
      return
    }

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
    }

    this.reconnectCount++
    const delay = Math.min(1000 * Math.pow(2, this.reconnectCount), 30000)

    console.log(`WebSocket reconnecting in ${delay}ms (attempt ${this.reconnectCount}/${this.maxReconnectCount})`)

    this.reconnectTimeout = setTimeout(() => {
      this.connect()
    }, delay)
  }

  startHeartbeat() {
    this.stopHeartbeat()
    this.heartbeatInterval = setInterval(() => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.send({ type: 'heartbeat', data: {} })
      }
    }, 30000) // 每30秒发送一次心跳
  }

  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data))
      return true
    } else {
      console.error('WebSocket is not connected, cannot send message')
      return false
    }
  }

  // 呼叫相关方法
  makeCall(phone, customerId = null) {
    return this.send({
      type: 'call_make',
      data: {
        phone,
        customer_id: customerId
      }
    })
  }

  answerCall() {
    return this.send({
      type: 'call_answer',
      data: {}
    })
  }

  hangupCall() {
    return this.send({
      type: 'call_hangup',
      data: {}
    })
  }

  holdCall() {
    return this.send({
      type: 'call_hold',
      data: {}
    })
  }

  resumeCall() {
    return this.send({
      type: 'call_resume',
      data: {}
    })
  }

  transferCall(targetUserId) {
    return this.send({
      type: 'call_transfer',
      data: {
        target_user_id: targetUserId
      }
    })
  }

  sendDTMF(digit) {
    return this.send({
      type: 'call_dtmf',
      data: {
        digit
      }
    })
  }

  // 事件处理
  handleCallStatus(status) {
    console.log('Call status updated:', status)
    // 可以在这里处理呼叫状态变更，比如更新UI
  }

  handleCallEvent(event) {
    console.log('Call event received:', event)

    // 根据不同事件类型显示通知
    switch (event.event) {
      case 'incoming_call':
        ElMessage.info({
          message: `有来电：${event.caller_number}`,
          duration: 0,
          showClose: true
        })
        break
      case 'call_connected':
        ElMessage.success('通话已接通')
        break
      case 'call_disconnected':
        ElMessage.info('通话已结束')
        break
      case 'call_failed':
        ElMessage.error(`呼叫失败：${event.reason || '未知错误'}`)
        break
    }
  }

  handleNotification(notification) {
    // 处理系统通知
    if (notification.type === 'success') {
      ElMessage.success(notification.message)
    } else if (notification.type === 'warning') {
      ElMessage.warning(notification.message)
    } else if (notification.type === 'error') {
      ElMessage.error(notification.message)
    } else {
      ElMessage.info(notification.message)
    }
  }

  // 事件监听
  on(event, callback) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, [])
    }
    this.eventListeners.get(event).push(callback)
  }

  off(event, callback) {
    if (!this.eventListeners.has(event)) {
      return
    }
    const callbacks = this.eventListeners.get(event)
    const index = callbacks.indexOf(callback)
    if (index > -1) {
      callbacks.splice(index, 1)
    }
  }

  emit(event, data) {
    if (!this.eventListeners.has(event)) {
      return
    }
    this.eventListeners.get(event).forEach(callback => {
      callback(data)
    })
  }

  close() {
    if (this.socket) {
      this.socket.close(1000, 'Normal closure')
      this.socket = null
    }
    this.stopHeartbeat()
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
      this.reconnectTimeout = null
    }
    this.eventListeners.clear()
  }
}

// 单例模式
const websocketService = new WebSocketService()

export default websocketService
