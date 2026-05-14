-- 初始化数据库脚本
-- 创建数据库如果不存在
CREATE DATABASE IF NOT EXISTS callcenter CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE callcenter;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    nickname VARCHAR(50),
    email VARCHAR(100),
    hashed_password VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    avatar VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建角色表
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建用户角色关联表
CREATE TABLE IF NOT EXISTS user_roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_role (user_id, role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建权限表
CREATE TABLE IF NOT EXISTS permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(20) NOT NULL COMMENT 'menu/button/api',
    parent_id INT DEFAULT 0,
    path VARCHAR(255),
    component VARCHAR(255),
    icon VARCHAR(50),
    sort INT DEFAULT 0,
    is_visible BOOLEAN DEFAULT TRUE,
    is_system BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_parent_id (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建角色权限关联表
CREATE TABLE IF NOT EXISTS role_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    UNIQUE KEY uk_role_permission (role_id, permission_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建系统配置表
CREATE TABLE IF NOT EXISTS system_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    description VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_config_key (config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入初始超级管理员用户（密码：123456）
INSERT INTO system_user (username, nickname, password, is_superuser, is_active) VALUES
('admin', '超级管理员', '$2b$12$LQ8Dw5b57jK3dR8p9S0tUuhVxUvN3X7hG6eH0kG5fD4eC3bA2S1D0', TRUE, TRUE)
ON DUPLICATE KEY UPDATE username=username;

-- 插入默认角色
INSERT INTO roles (name, description) VALUES
('admin', '系统管理员'),
('manager', '部门经理'),
('agent', '坐席人员')
ON DUPLICATE KEY UPDATE name=name;

-- 给管理员用户分配管理员角色
INSERT INTO user_roles (user_id, role_id)
SELECT 1, id FROM roles WHERE name = 'admin'
ON DUPLICATE KEY UPDATE user_id=user_id;

-- 插入默认权限配置
INSERT INTO permissions (name, code, type, path, component, icon, sort, is_visible, is_system) VALUES
-- 首页
('首页', 'dashboard:view', 'menu', '/dashboard', 'dashboard/index', 'Odometer', 1, 1, 1),
-- 客户管理
('客户管理', 'customer:view', 'menu', '/customer', 'customer/index', 'User', 2, 1, 1),
('客户列表', 'customer:list', 'menu', '/customer', 'customer/index', 'List', 1, 1, 1),
('新增客户', 'customer:create', 'button', '', '', '', 1, 0, 1),
('编辑客户', 'customer:update', 'button', '', '', '', 2, 0, 1),
('删除客户', 'customer:delete', 'button', '', '', '', 3, 0, 1),
('导入客户', 'customer:import', 'button', '', '', '', 4, 0, 1),
('导出客户', 'customer:export', 'button', '', '', '', 5, 0, 1),
-- 呼叫中心
('呼叫中心', 'call:view', 'menu', '/call', 'call/index', 'Phone', 3, 1, 1),
('外呼页面', 'call:agent', 'menu', '/call', 'call/index', 'Phone', 1, 1, 1),
('通话记录', 'call:record', 'menu', '/call/record', 'call/call-record', 'Document', 2, 1, 1),
('呼叫任务', 'call:task', 'menu', '/call/task', 'call/call-task', 'List', 3, 1, 1),
('话术管理', 'call:script', 'menu', '/call/script', 'call/script', 'ChatDotRound', 4, 1, 1),
-- 统计报表
('统计报表', 'report:view', 'menu', '/report', 'report/index', 'DataAnalysis', 4, 1, 1),
('通话趋势', 'report:call-trend', 'menu', '/report/call-trend', 'report/call-trend', 'TrendCharts', 1, 1, 1),
('坐席绩效', 'report:agent-performance', 'menu', '/report/agent-performance', 'report/agent-performance', 'UserFilled', 2, 1, 1),
('客户分析', 'report:customer-analysis', 'menu', '/report/customer-analysis', 'report/customer-analysis', 'User', 3, 1, 1),
-- 系统管理
('系统管理', 'system:view', 'menu', '/system', 'system/index', 'Setting', 99, 1, 1),
('用户管理', 'system:user', 'menu', '/system/user', 'system/user', 'User', 1, 1, 1),
('角色管理', 'system:role', 'menu', '/system/role', 'system/role', 'Avatar', 2, 1, 1),
('权限管理', 'system:permission', 'menu', '/system/permission', 'system/permission', 'Key', 3, 1, 1),
('系统配置', 'system:config', 'menu', '/system/config', 'system/config', 'Tools', 4, 1, 1),
('操作日志', 'system:logs', 'menu', '/system/logs', 'system/logs', 'Document', 5, 1, 1)
ON DUPLICATE KEY UPDATE code=code;

-- 给管理员角色分配所有权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p WHERE r.name = 'admin'
ON DUPLICATE KEY UPDATE role_id=role_id;

-- 插入默认系统配置
INSERT INTO system_config (config_key, config_value, description) VALUES
('system_name', '电话营销系统', '系统名称'),
('system_version', '1.0.0', '系统版本'),
('record_save_days', '180', '录音保存天数（天）'),
('auto_call_concurrent', '10', '自动外呼最大并发数'),
('call_timeout', '30', '呼叫超时时间（秒）')
ON DUPLICATE KEY UPDATE config_key=config_key;
