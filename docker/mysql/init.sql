-- 初始化数据库脚本
-- 创建数据库如果不存在
CREATE DATABASE IF NOT EXISTS callcenter CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE callcenter;

-- 创建用户表
CREATE TABLE IF NOT EXISTS system_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    nickname VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    avatar VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    department_id INT DEFAULT NULL,
    last_login_at DATETIME,
    last_login_ip VARCHAR(50),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建部门表
CREATE TABLE IF NOT EXISTS system_department (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INT DEFAULT 0,
    sort INT DEFAULT 0,
    leader VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    status BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建角色表
CREATE TABLE IF NOT EXISTS system_role (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    code VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255),
    sort INT DEFAULT 0,
    status BOOLEAN DEFAULT TRUE,
    data_scope INT DEFAULT 1,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建用户角色关联表
CREATE TABLE IF NOT EXISTS system_user_role (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES system_user(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES system_role(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_role (user_id, role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建权限表
CREATE TABLE IF NOT EXISTS system_permission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    code VARCHAR(100) NOT NULL UNIQUE,
    type INT DEFAULT 1 COMMENT '权限类型：1-菜单 2-按钮 3-接口',
    parent_id INT DEFAULT 0,
    path VARCHAR(255),
    component VARCHAR(255),
    icon VARCHAR(50),
    sort INT DEFAULT 0,
    status BOOLEAN DEFAULT TRUE,
    visible BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_parent_id (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建角色权限关联表
CREATE TABLE IF NOT EXISTS system_role_permission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES system_role(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES system_permission(id) ON DELETE CASCADE,
    UNIQUE KEY uk_role_permission (role_id, permission_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建操作日志表
CREATE TABLE IF NOT EXISTS system_operation_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    username VARCHAR(50),
    module VARCHAR(50),
    operation VARCHAR(100),
    method VARCHAR(10),
    path VARCHAR(255),
    ip VARCHAR(50),
    location VARCHAR(100),
    user_agent VARCHAR(255),
    request_params JSON,
    response_result JSON,
    status INT DEFAULT 1,
    error_msg TEXT,
    cost_time INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建系统配置表
CREATE TABLE IF NOT EXISTS system_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(100) NOT NULL UNIQUE,
    `value` TEXT NOT NULL,
    name VARCHAR(100),
    description VARCHAR(255),
    type INT DEFAULT 1,
    sort INT DEFAULT 0,
    is_public BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_config_key (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入初始超级管理员用户（密码：123456）
INSERT INTO system_user (username, nickname, password, is_superuser, is_active) VALUES
('admin', '超级管理员', '$2b$12$LQ8Dw5b57jK3dR8p9S0tUuhVxUvN3X7hG6eH0kG5fD4eC3bA2S1D0', TRUE, TRUE)
ON DUPLICATE KEY UPDATE username=username;

-- 插入默认角色
INSERT INTO system_role (name, code, description, sort, status) VALUES
('admin', 'admin', '系统管理员', 1, 1),
('manager', 'manager', '部门经理', 2, 1),
('agent', 'agent', '坐席人员', 3, 1)
ON DUPLICATE KEY UPDATE name=name;

-- 给管理员用户分配管理员角色
INSERT INTO system_user_role (user_id, role_id)
SELECT 1, id FROM system_role WHERE code = 'admin'
ON DUPLICATE KEY UPDATE user_id=user_id;

-- 插入默认权限配置
INSERT INTO system_permission (name, code, type, path, component, icon, sort, visible, status) VALUES
-- 首页
('首页', 'dashboard:view', 1, '/dashboard', 'dashboard/index', 'Odometer', 1, 1, 1),
-- 客户管理
('客户管理', 'customer:view', 1, '/customer', 'customer/index', 'User', 2, 1, 1),
('客户列表', 'customer:list', 1, '/customer', 'customer/index', 'List', 1, 1, 1),
('新增客户', 'customer:create', 2, '', '', '', 1, 0, 1),
('编辑客户', 'customer:update', 2, '', '', '', 2, 0, 1),
('删除客户', 'customer:delete', 2, '', '', '', 3, 0, 1),
('导入客户', 'customer:import', 2, '', '', '', 4, 0, 1),
('导出客户', 'customer:export', 2, '', '', '', 5, 0, 1),
-- 呼叫中心
('呼叫中心', 'call:view', 1, '/call', 'call/index', 'Phone', 3, 1, 1),
('外呼页面', 'call:agent', 1, '/call', 'call/index', 'Phone', 1, 1, 1),
('通话记录', 'call:record', 1, '/call/record', 'call/call-record', 'Document', 2, 1, 1),
('呼叫任务', 'call:task', 1, '/call/task', 'call/call-task', 'List', 3, 1, 1),
('话术管理', 'call:script', 1, '/call/script', 'call/script', 'ChatDotRound', 4, 1, 1),
-- 统计报表
('统计报表', 'report:view', 1, '/report', 'report/index', 'DataAnalysis', 4, 1, 1),
('通话趋势', 'report:call-trend', 1, '/report/call-trend', 'report/call-trend', 'TrendCharts', 1, 1, 1),
('坐席绩效', 'report:agent-performance', 1, '/report/agent-performance', 'report/agent-performance', 'UserFilled', 2, 1, 1),
('客户分析', 'report:customer-analysis', 1, '/report/customer-analysis', 'report/customer-analysis', 'User', 3, 1, 1),
-- 系统管理
('系统管理', 'system:view', 1, '/system', 'system/index', 'Setting', 99, 1, 1),
('用户管理', 'system:user', 1, '/system/user', 'system/user', 'User', 1, 1, 1),
('角色管理', 'system:role', 1, '/system/role', 'system/role', 'Avatar', 2, 1, 1),
('权限管理', 'system:permission', 1, '/system/permission', 'system/permission', 'Key', 3, 1, 1),
('系统配置', 'system:config', 1, '/system/config', 'system/config', 'Tools', 4, 1, 1),
('操作日志', 'system:logs', 1, '/system/logs', 'system/logs', 'Document', 5, 1, 1)
ON DUPLICATE KEY UPDATE code=code;

-- 给管理员角色分配所有权限
INSERT INTO system_role_permission (role_id, permission_id)
SELECT r.id, p.id FROM system_role r, system_permission p WHERE r.code = 'admin'
ON DUPLICATE KEY UPDATE role_id=role_id;

-- 插入默认系统配置
INSERT INTO system_config (`key`, `value`, name, description, type, sort, is_public) VALUES
('system_name', '电话营销系统', '系统名称', '系统显示名称', 1, 1, 1),
('system_version', '1.0.0', '系统版本', '当前系统版本号', 1, 2, 1),
('record_save_days', '180', '录音保存天数', '通话录音文件保存天数', 2, 3, 0),
('auto_call_concurrent', '10', '自动外呼最大并发数', '自动外呼任务同时执行的最大呼叫数', 2, 4, 0),
('call_timeout', '30', '呼叫超时时间', '外呼呼叫超时时间（秒）', 2, 5, 0)
ON DUPLICATE KEY UPDATE `key`=`key`;
