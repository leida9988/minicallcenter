# 电话营销系统 - 前端
基于 Vue 3 + Element Plus 开发的电话营销系统前端界面。
## 技术栈
- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **UI 框架**: Element Plus
- **路由**: Vue Router
- **状态管理**: Pinia + pinia-plugin-persistedstate
- **HTTP 客户端**: Axios
- **图表库**: ECharts
- **工具库**: Dayjs
## 功能模块
- 🏠 **首页看板**: 数据统计展示、通话趋势、客户分析
- 👥 **客户管理**: 客户信息管理、跟进记录、公海管理
- 📞 **呼叫中心**: 外呼功能、通话记录、呼叫任务、话术管理
- 📊 **统计报表**: 通话趋势、坐席绩效、客户分析
- ⚙️ **系统管理**: 用户管理、角色权限、系统配置、操作日志
- 👤 **个人中心**: 个人信息、修改密码
## 项目结构
```
├── public/          # 静态资源
├── src/
│   ├── api/         # API 接口
│   ├── components/  # 公共组件
│   ├── layout/      # 布局组件
│   ├── router/      # 路由配置
│   ├── store/       # 状态管理
│   ├── styles/      # 全局样式
│   ├── utils/       # 工具函数
│   ├── views/       # 页面组件
│   ├── App.vue      # 根组件
│   └── main.js      # 入口文件
├── .env.development # 开发环境配置
├── .env.production  # 生产环境配置
├── vite.config.js   # Vite 配置
└── package.json     # 依赖配置
```
## 开发环境搭建
### 安装依赖
```bash
npm install
```
### 启动开发服务
```bash
npm run dev
```
访问 http://localhost:5173
### 生产构建
```bash
npm run build
```
### 预览构建产物
```bash
npm run preview
```
## 开发规范
### 代码风格
- 使用 Composition API
- 组件使用 `.vue` 单文件组件
- 变量命名使用小驼峰
- 组件命名使用大驼峰
### 目录规范
- API 接口按模块放到 `src/api/` 目录下
- 公共组件放到 `src/components/` 目录下
- 工具函数放到 `src/utils/` 目录下
- 页面组件按模块放到 `src/views/` 目录下
### 环境变量
- 环境变量配置在根目录的 `.env.*` 文件中
- 环境变量必须以 `VITE_` 为前缀才能在前端代码中使用
## 部署说明
### Nginx 配置示例
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/dist;
    index index.html;
    # 前端路由 history 模式配置
    location / {
        try_files $uri $uri/ /index.html;
    }
    # API 代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```
## 浏览器支持
- Chrome >= 87
- Edge >= 88
- Firefox >= 78
- Safari >= 14
## License
MIT
