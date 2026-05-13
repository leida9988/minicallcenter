import request from '@/utils/request'
// 获取客户列表
export function getCustomerListApi(params) {
  return request({
    url: '/v1/customer/list',
    method: 'get',
    params
  })
}
// 获取我的客户列表
export function getMyCustomerListApi(params) {
  return request({
    url: '/v1/customer/my-list',
    method: 'get',
    params
  })
}
// 获取客户详情
export function getCustomerDetailApi(id) {
  return request({
    url: `/v1/customer/${id}`,
    method: 'get'
  })
}
// 创建客户
export function createCustomerApi(data) {
  return request({
    url: '/v1/customer/create',
    method: 'post',
    data
  })
}
// 更新客户
export function updateCustomerApi(id, data) {
  return request({
    url: `/v1/customer/update/${id}`,
    method: 'put',
    data
  })
}
// 删除客户
export function deleteCustomerApi(id) {
  return request({
    url: `/v1/customer/delete/${id}`,
    method: 'delete'
  })
}
// 批量分配客户
export function assignCustomerApi(data) {
  return request({
    url: '/v1/customer/assign',
    method: 'post',
    data
  })
}
// 回收客户到公海
export function recycleCustomerApi(id) {
  return request({
    url: `/v1/customer/recycle/${id}`,
    method: 'post'
  })
}
// 批量回收客户
export function batchRecycleCustomerApi(data) {
  return request({
    url: '/v1/customer/batch-recycle',
    method: 'post',
    data
  })
}
// 导入客户
export function importCustomerApi(data) {
  return request({
    url: '/v1/customer/import',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
// 导出客户
export function exportCustomerApi(params) {
  return request({
    url: '/v1/customer/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}
// 获取跟进记录列表
export function getFollowRecordListApi(params) {
  return request({
    url: '/v1/customer/follow-record/list',
    method: 'get',
    params
  })
}
// 创建跟进记录
export function createFollowRecordApi(data) {
  return request({
    url: '/v1/customer/follow-record/create',
    method: 'post',
    data
  })
}
// 删除跟进记录
export function deleteFollowRecordApi(id) {
  return request({
    url: `/v1/customer/follow-record/delete/${id}`,
    method: 'delete'
  })
}
// 获取标签列表
export function getTagListApi(params) {
  return request({
    url: '/v1/customer/tag/list',
    method: 'get',
    params
  })
}
// 创建标签
export function createTagApi(data) {
  return request({
    url: '/v1/customer/tag/create',
    method: 'post',
    data
  })
}
// 更新标签
export function updateTagApi(id, data) {
  return request({
    url: `/v1/customer/tag/update/${id}`,
    method: 'put',
    data
  })
}
// 删除标签
export function deleteTagApi(id) {
  return request({
    url: `/v1/customer/tag/delete/${id}`,
    method: 'delete'
  })
}
// 获取客户统计
export function getCustomerStatisticsApi() {
  return request({
    url: '/v1/customer/statistics',
    method: 'get'
  })
}
