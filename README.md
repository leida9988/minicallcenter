# 通用型中小型电话营销系统

面向50坐席以内、日外呼量10000次以下的中小企业，提供轻量化、易部署、可扩展的通用型电话营销解决方案。

## ✨ 功能特性

### 📞 呼叫中心
- 支持手动拨号、批量导入外呼、自动外呼三种模式
- 外呼号码池管理，自动轮询主叫号码
- 通话控制：接听、挂断、静音、保持、恢复、三方通话、通话转接
- 坐席状态管理：空闲、忙碌、通话中、离线、小憩
- 通话全程自动录音，支持双声道录音
- 录音文件在线播放、下载、检索
- 呼入管理：IVR语音导航、来电弹屏、技能组分配
- 完整的通话记录和统计分析

### 👥 客户管理
- 支持自定义客户字段，满足不同行业需求
- 批量导入导出客户数据
- 客户资料去重、合并
- 线索分配：手动分配、自动分配（按坐席负载、地域、客户标签）
- 线索回收机制，未跟进线索自动回流公海
- 公海池管理，支持多公海池配置
- 跟进记录管理，支持文本、语音、图片等多种形式
- 跟进任务提醒，支持设置下次跟进时间
- 客户标签体系，支持手动打标和自动打标

### 📊 统计分析
- 呼叫数据统计：外呼总量、接通率、平均通话时长、峰值并发数
- 坐席绩效报表：外呼量、接通量、通话时长、有效沟通率、转化率、成单量
- 转化率分析：线索转化率、跟进转化率、成单转化率
- 转化漏斗分析，各环节流失原因统计
- 话术效果分析，高转化话术关键词提取和推荐

### 🛠️ 系统管理
- 基于角色的权限控制（RBAC），支持多角色配置
- 组织架构管理，支持多级部门和技能组配置
- 完整的操作日志记录，不可删除篡改
- 灵活的系统配置：呼叫参数、录音参数、外呼规则等
- 字段配置引擎，支持业务字段动态扩展
- 流程配置引擎，支持业务流程自定义
- 话术管理，支持智能推荐

### 🤖 AI能力
- ASR语音识别：通话录音自动转写
- TTS语音合成：文本转语音播放
- 大模型接口：话术推荐、应答建议、会话总结
- 智能外呼接口：支持全自动AI坐席外呼
- 智能质检：自动识别违规话术、情绪分析
- 插件化设计，支持多个AI厂商接入

### 🖥️ 坐席端
- 基于Electron的桌面端应用，使用体验更佳
- 全局快捷键支持：快速接听、挂断
- 系统通知：来电提醒、消息通知
- 自动登录，记住登录状态
- 最小化到托盘，不占用任务栏空间

## 🚀 快速部署

### 环境要求
- Docker 20.10+
- Docker Compose 2.0+
- 服务器配置：4核8G以上，硬盘500G以上（根据录音保存时长调整）
- 操作系统：Linux (推荐Ubuntu 20.04/CentOS 7+) / Windows / macOS

### 部署步骤

1. **下载项目代码**
```bash
git clone <项目地址>
cd callcenter
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，根据实际情况修改配置
vim .env
```

3. **启动服务**
```bash
# 第一次启动会自动构建镜像，需要等待几分钟
docker-compose up -d
```

4. **访问系统**
- 前端地址：http://服务器IP
- 默认账号：admin / admin123
- API文档地址：http://服务器IP:8000/docs

### 常用命令
```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f [服务名]

# 停止服务
docker-compose stop

# 重启服务
docker-compose restart [服务名]

# 升级版本
git pull
docker-compose up -d --build

# 数据备份
docker exec callcenter-mysql mysqldump -u root -p<数据库密码> callcenter > backup.sql
```

## 🔧 开发环境搭建

### 后端开发
```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，配置数据库、Redis等信息

# 启动开发服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务
npm run dev

# 构建生产版本
npm run build
```

### 桌面端开发
```bash
# 进入桌面端目录
cd electron

# 安装依赖
npm install

# 启动开发模式
npm run dev

# 构建Windows安装包
npm run build:win

# 构建Mac安装包
npm run build:mac

# 构建Linux安装包
npm run build:linux
```

## 📁 项目结构
```
callcenter
├── backend                 # 后端服务
│   ├── app                 # 应用代码
│   │   ├── api             # API接口
│   │   ├── core            # 核心模块
│   │   ├── models          # 数据模型
│   │   ├── services        # 业务逻辑
│   │   └── utils           # 工具函数
│   ├── Dockerfile          # 后端Dockerfile
│   └── requirements.txt    # Python依赖
├── frontend                # 前端页面
│   ├── src                 # 源代码
│   │   ├── views           # 页面组件
│   │   ├── components      # 公共组件
│   │   ├── router          # 路由配置
│   │   ├── store           # 状态管理
│   │   └── utils           # 工具函数
│   ├── Dockerfile          # 前端Dockerfile
│   └── nginx.conf          # Nginx配置
├── electron                # 桌面端应用
│   ├── main.js             # 主进程代码
│   ├── preload.js          # 预加载脚本
│   └── package.json        # 项目配置
├── docker                  # Docker相关配置
│   └── mysql               # MySQL初始化脚本
├── docker-compose.yml      # Docker Compose配置
├── .env.example            # 环境变量示例
└── README.md               # 项目说明文档
```

## 🤝 技术栈

### 后端
- **Web框架**: FastAPI (Python)
- **数据库**: MySQL 8.0 + SQLAlchemy ORM
- **缓存**: Redis 7.x
- **电话交换**: FreeSWITCH
- **认证**: JWT + OAuth2
- **权限**: Casbin RBAC
- **AI接口**: 抽象层，支持阿里云、百度智能云、OpenAI等

### 前端
- **框架**: Vue 3 + Vite
- **UI组件**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **图表**: ECharts
- **工具库**: Axios + Day.js

### 桌面端
- **框架**: Electron
- **打包**: electron-builder
- **本地存储**: electron-store

### 部署
- **容器化**: Docker + Docker Compose
- **Web服务器**: Nginx
- **监控**: Prometheus + Grafana (可选)

## 📋 系统要求

### 服务器配置

#### 最小配置（10坐席以内）
- CPU: 4核
- 内存: 8G
- 硬盘: 500G SSD
- 带宽: 10M

#### 推荐配置（30-50坐席）
- CPU: 8核
- 内存: 16G
- 硬盘: 2T SSD
- 带宽: 50M

### 客户端要求
- Windows 10+ / macOS 10.15+ / Linux
- 浏览器: Chrome 90+ / Edge 90+ / Firefox 88+
- 耳麦：建议使用USB耳麦，音质更好

## ⚙️ 对接说明

### 线路对接
系统支持标准SIP线路对接，需要运营商提供：
- SIP服务器地址和端口
- SIP账号和密码
- 主叫号码池

### AI能力对接
系统已经内置了阿里云AI能力的对接，也可以自定义扩展其他厂商：
- ASR语音识别
- TTS语音合成
- 大模型服务

## 📄 许可证

MIT License

## 🤝 技术支持

如有问题或需要商业支持，请联系开发者。
