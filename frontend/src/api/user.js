import request from '@/utils/request'
// 登录
export function loginApi(data) {
  return request({
    url: '/v1/auth/login',
    method: 'post',
    data
  })
}
// 登出
export function logoutApi() {
  return request({
    url: '/v1/auth/logout',
    method: 'post'
  })
}
// 获取用户信息
export function getUserInfoApi() {
  return request({
    url: '/v1/user/info',
    method: 'get'
  })
}
// 获取用户列表
export function getUserListApi(params) {
  return request({
    url: '/v1/user/list',
    method: 'get',
    params
  })
}
// 创建用户
export function createUserApi(data) {
  return request({
    url: '/v1/user/create',
    method: 'post',
    data
  })
}
// 更新用户
export function updateUserApi(id, data) {
  return request({
    url: `/v1/user/update/${id}`,
    method: 'put',
    data
  })
}
// 删除用户
export function deleteUserApi(id) {
  return request({
    url: `/v1/user/delete/${id}`,
    method: 'delete'
  })
}
// 重置用户密码
export function resetUserPasswordApi(id, data) {
  return request({
    url: `/v1/user/reset-password/${id}`,
    method: 'post',
    data
  })
}
// 修改当前用户密码
export function changePasswordApi(data) {
  return request({
    url: '/v1/user/change-password',
    method: 'put',
    data
  })
}
// 更新个人信息
export function updateProfileApi(data) {
  return request({
    url: '/v1/user/profile/update',
    method: 'put',
    data
  })
}
