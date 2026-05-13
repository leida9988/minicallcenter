const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  // 登录信息相关
  saveLoginInfo: (data) => ipcRenderer.invoke('save-login-info', data),
  clearLoginInfo: () => ipcRenderer.invoke('clear-login-info'),
  onAutoLogin: (callback) => ipcRenderer.on('auto-login', (event, data) => callback(data)),

  // 设置相关
  getSettings: () => ipcRenderer.invoke('get-settings'),
  saveSettings: (settings) => ipcRenderer.invoke('save-settings', settings),

  // 通知相关
  showIncomingCallNotification: (data) => ipcRenderer.send('incoming-call-notification', data),
  showMessageNotification: (data) => ipcRenderer.send('message-notification', data),

  // 快捷键相关
  onShortcutAnswerCall: (callback) => ipcRenderer.on('shortcut-answer-call', callback),
  onShortcutHangupCall: (callback) => ipcRenderer.on('shortcut-hangup-call', callback),

  // 移除监听
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
})
