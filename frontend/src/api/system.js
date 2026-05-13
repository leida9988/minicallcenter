import request from '@/utils/request'
// 获取角色列表
export function getRoleListApi(params) {
  return request({
    url: '/v1/role/list',
    method: 'get',
    params
  })
}
// 获取所有角色
export function getAllRolesApi() {
  return request({
    url: '/v1/role/all',
    method: 'get'
  })
}
// 获取角色详情
export function getRoleDetailApi(id) {
  return request({
    url: `/v1/role/${id}`,
    method: 'get'
  })
}
// 创建角色
export function createRoleApi(data) {
  return request({
    url: '/v1/role/create',
    method: 'post',
    data
  })
}
// 更新角色
export function updateRoleApi(id, data) {
  return request({
    url: `/v1/role/update/${id}`,
    method: 'put',
    data
  })
}
// 删除角色
export function deleteRoleApi(id) {
  return request({
    url: `/v1/role/delete/${id}`,
    method: 'delete'
  })
}
// 获取角色权限ID列表
export function getRolePermissionIdsApi(id) {
  return request({
    url: `/v1/role/permissions/${id}`,
    method: 'get'
  })
}
// 分配角色权限
export function assignRolePermissionsApi(data) {
  return request({
    url: '/v1/role/assign-permissions',
    method: 'post',
    data
  })
}
// 获取权限树
export function getPermissionTreeApi() {
  return request({
    url: '/v1/permission/tree',
    method: 'get'
  })
}
// 获取完整权限树
export function getAllPermissionTreeApi() {
  return request({
    url: '/v1/permission/all-tree',
    method: 'get'
  })
}
// 获取权限列表
export function getPermissionListApi(params) {
  return request({
    url: '/v1/permission/list',
    method: 'get',
    params
  })
}
// 获取权限详情
export function getPermissionDetailApi(id) {
  return request({
    url: `/v1/permission/${id}`,
    method: 'get'
  })
}
// 创建权限
export function createPermissionApi(data) {
  return request({
    url: '/v1/permission/create',
    method: 'post',
    data
  })
}
// 更新权限
export function updatePermissionApi(id, data) {
  return request({
    url: `/v1/permission/update/${id}`,
    method: 'put',
    data
  })
}
// 删除权限
export function deletePermissionApi(id) {
  return request({
    url: `/v1/permission/delete/${id}`,
    method: 'delete'
  })
}
// 获取权限编码列表
export function getPermissionCodesApi() {
  return request({
    url: '/v1/permission/codes/me',
    method: 'get'
  })
}
// 获取系统配置列表
export function getSystemConfigListApi(params) {
  return request({
    url: '/v1/system/config/list',
    method: 'get',
    params
  })
}
// 获取所有系统配置
export function getAllSystemConfigsApi() {
  return request({
    url: '/v1/system/config/all',
    method: 'get'
  })
}
// 获取公开系统配置
export function getPublicSystemConfigApi() {
  return request({
    url: '/v1/system/config/public',
    method: 'get'
  })
}
// 获取系统配置详情
export function getSystemConfigDetailApi(id) {
  return request({
    url: `/v1/system/config/${id}`,
    method: 'get'
  })
}
// 创建系统配置
export function createSystemConfigApi(data) {
  return request({
    url: '/v1/system/config/create',
    method: 'post',
    data
  })
}
// 更新系统配置
export function updateSystemConfigApi(id, data) {
  return request({
    url: `/v1/system/config/update/${id}`,
    method: 'put',
    data
  })
}
// 删除系统配置
export function deleteSystemConfigApi(id) {
  return request({
    url: `/v1/system/config/delete/${id}`,
    method: 'delete'
  })
}
// 批量更新系统配置
export function batchUpdateSystemConfigApi(data) {
  return request({
    url: '/v1/system/config/batch-update',
    method: 'put',
    data
  })
}
// 获取系统信息
export function getSystemInfoApi() {
  return request({
    url: '/v1/system/info',
    method: 'get'
  })
}
// 获取系统状态
export function getSystemStatusApi() {
  return request({
    url: '/v1/system/status',
    method: 'get'
  })
}
