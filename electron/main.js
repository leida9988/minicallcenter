const { app, BrowserWindow, ipcMain, Tray, Menu, Notification, globalShortcut, shell } = require('electron')
const path = require('path')
const Store = require('electron-store')

// 初始化配置存储
const store = new Store()

let mainWindow = null
let tray = null
let isQuitting = false

// 单实例锁
const gotTheLock = app.requestSingleInstanceLock()
if (!gotTheLock) {
  app.quit()
  return
}

app.on('second-instance', (event, commandLine, workingDirectory) => {
  // 当运行第二个实例时，聚焦到主窗口
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore()
    mainWindow.focus()
  }
})

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 1000,
    minHeight: 700,
    title: '电话营销系统 - 坐席端',
    icon: path.join(__dirname, 'assets/icon.ico'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true
    },
    show: false // 先隐藏，等页面加载完成后再显示
  })

  // 加载前端页面
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173')
    // 打开开发者工具
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../frontend/dist/index.html'))
  }

  // 页面加载完成后显示窗口
  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
    mainWindow.focus()

    // 检查是否有保存的登录信息，如果有自动登录
    const token = store.get('token')
    const userInfo = store.get('userInfo')
    if (token && userInfo) {
      mainWindow.webContents.send('auto-login', { token, userInfo })
    }
  })

  // 关闭窗口前确认
  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault()
      mainWindow.hide()

      // 显示通知
      if (Notification.isSupported()) {
        new Notification({
          title: '程序已最小化到托盘',
          body: '点击托盘图标可以重新打开程序'
        }).show()
      }
    }
    return false
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })

  // 打开新窗口时使用系统默认浏览器
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })
}

// 创建系统托盘
function createTray() {
  tray = new Tray(path.join(__dirname, 'assets/icon.ico'))

  const contextMenu = Menu.buildFromTemplate([
    {
      label: '打开主界面',
      click: () => {
        if (mainWindow) {
          mainWindow.show()
          mainWindow.focus()
        }
      }
    },
    {
      label: '来电提醒',
      type: 'checkbox',
      checked: store.get('settings.notification.call', true),
      click: (menuItem) => {
        store.set('settings.notification.call', menuItem.checked)
      }
    },
    {
      label: '消息提醒',
      type: 'checkbox',
      checked: store.get('settings.notification.message', true),
      click: (menuItem) => {
        store.set('settings.notification.message', menuItem.checked)
      }
    },
    {
      type: 'separator'
    },
    {
      label: '退出程序',
      click: () => {
        isQuitting = true
        app.quit()
      }
    }
  ])

  tray.setToolTip('电话营销系统 - 坐席端')
  tray.setContextMenu(contextMenu)

  // 点击托盘图标显示窗口
  tray.on('click', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide()
      } else {
        mainWindow.show()
        mainWindow.focus()
      }
    }
  })
}

// 注册全局快捷键
function registerGlobalShortcuts() {
  // 接听电话快捷键：Ctrl+Alt+A
  globalShortcut.register('Ctrl+Alt+A', () => {
    if (mainWindow) {
      mainWindow.show()
      mainWindow.focus()
      mainWindow.webContents.send('shortcut-answer-call')
    }
  })

  // 挂断电话快捷键：Ctrl+Alt+S
  globalShortcut.register('Ctrl+Alt+S', () => {
    if (mainWindow) {
      mainWindow.webContents.send('shortcut-hangup-call')
    }
  })

  // 打开/隐藏窗口快捷键：Ctrl+Alt+Z
  globalShortcut.register('Ctrl+Alt+Z', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide()
      } else {
        mainWindow.show()
        mainWindow.focus()
      }
    }
  })
}

app.whenReady().then(() => {
  createWindow()
  createTray()
  registerGlobalShortcuts()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('will-quit', () => {
  // 注销所有快捷键
  globalShortcut.unregisterAll()
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// IPC通信处理
ipcMain.handle('save-login-info', (event, { token, userInfo }) => {
  store.set('token', token)
  store.set('userInfo', userInfo)
  return { success: true }
})

ipcMain.handle('clear-login-info', () => {
  store.delete('token')
  store.delete('userInfo')
  return { success: true }
})

ipcMain.handle('get-settings', () => {
  return store.get('settings', {
    notification: {
      call: true,
      message: true
    },
    autoAnswer: false,
    autoPopup: true
  })
})

ipcMain.handle('save-settings', (event, settings) => {
  store.set('settings', settings)
  return { success: true }
})

// 来电通知
ipcMain.on('incoming-call-notification', (event, data) => {
  const callNotificationEnabled = store.get('settings.notification.call', true)
  if (!callNotificationEnabled || !Notification.isSupported()) {
    return
  }

  const notification = new Notification({
    title: '来电提醒',
    body: `来电号码：${data.phoneNumber}\n客户姓名：${data.customerName || '未知客户'}`,
    icon: path.join(__dirname, 'assets/call.ico'),
    silent: false,
    timeoutType: 'never'
  })

  notification.on('click', () => {
    if (mainWindow) {
      mainWindow.show()
      mainWindow.focus()
    }
  })

  notification.show()

  // 保存notification引用，防止被垃圾回收
  event.sender._notification = notification
})

// 消息通知
ipcMain.on('message-notification', (event, data) => {
  const messageNotificationEnabled = store.get('settings.notification.message', true)
  if (!messageNotificationEnabled || !Notification.isSupported()) {
    return
  }

  const notification = new Notification({
    title: data.title || '新消息',
    body: data.content,
    icon: path.join(__dirname, 'assets/message.ico')
  })

  notification.show()
})
