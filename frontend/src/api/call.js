import request from '@/utils/request'
// 发起外呼
export function makeCallApi(data) {
  return request({
    url: '/v1/call/outbound',
    method: 'post',
    data
  })
}
// 通话控制
export function callControlApi(data) {
  return request({
    url: '/v1/call/control',
    method: 'post',
    data
  })
}
// 获取通话状态
export function getCallStatusApi(callId) {
  return request({
    url: `/v1/call/status/${callId}`,
    method: 'get'
  })
}
// 获取通话记录列表
export function getCallRecordListApi(params) {
  return request({
    url: '/v1/call/record/list',
    method: 'get',
    params
  })
}
// 获取我的通话记录
export function getMyCallRecordListApi(params) {
  return request({
    url: '/v1/call/record/my-list',
    method: 'get',
    params
  })
}
// 获取通话记录详情
export function getCallRecordDetailApi(id) {
  return request({
    url: `/v1/call/record/${id}`,
    method: 'get'
  })
}
// 删除通话记录
export function deleteCallRecordApi(id) {
  return request({
    url: `/v1/call/record/delete/${id}`,
    method: 'delete'
  })
}
// 下载通话录音
export function downloadRecordingApi(id) {
  return request({
    url: `/v1/call/record/download/${id}`,
    method: 'get',
    responseType: 'blob'
  })
}
// 获取呼叫任务列表
export function getCallTaskListApi(params) {
  return request({
    url: '/v1/call/task/list',
    method: 'get',
    params
  })
}
// 获取我的呼叫任务
export function getMyCallTaskListApi(params) {
  return request({
    url: '/v1/call/task/my-list',
    method: 'get',
    params
  })
}
// 创建呼叫任务
export function createCallTaskApi(data) {
  return request({
    url: '/v1/call/task/create',
    method: 'post',
    data
  })
}
// 控制呼叫任务
export function controlCallTaskApi(data) {
  return request({
    url: '/v1/call/task/control',
    method: 'post',
    data
  })
}
// 删除呼叫任务
export function deleteCallTaskApi(id) {
  return request({
    url: `/v1/call/task/delete/${id}`,
    method: 'delete'
  })
}
// 获取话术分类列表
export function getScriptCategoryListApi() {
  return request({
    url: '/v1/call/script/category/list',
    method: 'get'
  })
}
// 创建话术分类
export function createScriptCategoryApi(data) {
  return request({
    url: '/v1/call/script/category/create',
    method: 'post',
    data
  })
}
// 获取话术列表
export function getScriptListApi(params) {
  return request({
    url: '/v1/call/script/list',
    method: 'get',
    params
  })
}
// 获取分类下的话术
export function getScriptsByCategoryApi(categoryId) {
  return request({
    url: `/v1/call/script/category/${categoryId}`,
    method: 'get'
  })
}
// 创建话术
export function createScriptApi(data) {
  return request({
    url: '/v1/call/script/create',
    method: 'post',
    data
  })
}
// 更新话术
export function updateScriptApi(id, data) {
  return request({
    url: `/v1/call/script/update/${id}`,
    method: 'put',
    data
  })
}
// 删除话术
export function deleteScriptApi(id) {
  return request({
    url: `/v1/call/script/delete/${id}`,
    method: 'delete'
  })
}
// 获取主叫号码列表
export function getCallerNumberListApi() {
  return request({
    url: '/v1/call/caller-number/list',
    method: 'get'
  })
}
// 创建主叫号码
export function createCallerNumberApi(data) {
  return request({
    url: '/v1/call/caller-number/create',
    method: 'post',
    data
  })
}
// 删除主叫号码
export function deleteCallerNumberApi(id) {
  return request({
    url: `/v1/call/caller-number/delete/${id}`,
    method: 'delete'
  })
}
// 获取技能组列表
export function getSkillGroupListApi() {
  return request({
    url: '/v1/call/skill-group/list',
    method: 'get'
  })
}
// 创建技能组
export function createSkillGroupApi(data) {
  return request({
    url: '/v1/call/skill-group/create',
    method: 'post',
    data
  })
}
// 更新技能组
export function updateSkillGroupApi(id, data) {
  return request({
    url: `/v1/call/skill-group/update/${id}`,
    method: 'put',
    data
  })
}
// 删除技能组
export function deleteSkillGroupApi(id) {
  return request({
    url: `/v1/call/skill-group/delete/${id}`,
    method: 'delete'
  })
}
// 获取黑名单列表
export function getBlackListApi(params) {
  return request({
    url: '/v1/call/black-list/list',
    method: 'get',
    params
  })
}
// 添加黑名单
export function createBlackListApi(data) {
  return request({
    url: '/v1/call/black-list/create',
    method: 'post',
    data
  })
}
// 删除黑名单
export function deleteBlackListApi(id) {
  return request({
    url: `/v1/call/black-list/delete/${id}`,
    method: 'delete'
  })
}
// 检查号码是否在黑名单
export function checkBlackListApi(phone) {
  return request({
    url: '/v1/call/black-list/check',
    method: 'post',
    data: { phone }
  })
}
// 获取IVR配置列表
export function getIVRConfigListApi() {
  return request({
    url: '/v1/call/ivr/list',
    method: 'get'
  })
}
// 创建IVR配置
export function createIVRConfigApi(data) {
  return request({
    url: '/v1/call/ivr/create',
    method: 'post',
    data
  })
}
// 更新IVR配置
export function updateIVRConfigApi(id, data) {
  return request({
    url: `/v1/call/ivr/update/${id}`,
    method: 'put',
    data
  })
}
// 删除IVR配置
export function deleteIVRConfigApi(id) {
  return request({
    url: `/v1/call/ivr/delete/${id}`,
    method: 'delete'
  })
}
// 获取通话统计
export function getCallStatisticsApi(params) {
  return request({
    url: '/v1/call/statistics',
    method: 'get',
    params
  })
}
// 挂断电话
export function hangupCallApi(data) {
  return request({
    url: '/v1/call/hangup',
    method: 'post',
    data
  })
}
// 切换静音
export function toggleMuteApi(data) {
  return request({
    url: '/v1/call/toggle-mute',
    method: 'post',
    data
  })
}
// 切换保持
export function toggleHoldApi(data) {
  return request({
    url: '/v1/call/toggle-hold',
    method: 'post',
    data
  })
}
// 通话转接
export function transferCallApi(data) {
  return request({
    url: '/v1/call/transfer',
    method: 'post',
    data
  })
}
// 三方通话
export function threeWayCallApi(data) {
  return request({
    url: '/v1/call/three-way',
    method: 'post',
    data
  })
}
// 更新坐席状态
export function updateAgentStatusApi(data) {
  return request({
    url: '/v1/call/agent/status',
    method: 'post',
    data
  })
}
// 更新呼叫任务
export function updateCallTaskApi(id, data) {
  return request({
    url: `/v1/call/task/update/${id}`,
    method: 'put',
    data
  })
}
// 启动呼叫任务
export function startCallTaskApi(id) {
  return request({
    url: `/v1/call/task/start/${id}`,
    method: 'post'
  })
}
// 暂停呼叫任务
export function pauseCallTaskApi(id) {
  return request({
    url: `/v1/call/task/pause/${id}`,
    method: 'post'
  })
}
// 取消呼叫任务
export function cancelCallTaskApi(id) {
  return request({
    url: `/v1/call/task/cancel/${id}`,
    method: 'post'
  })
}
// 导出通话记录
export function exportCallRecordApi(params) {
  return request({
    url: '/v1/call/record/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}
// 切换话术状态
export function toggleScriptStatusApi(id, data) {
  return request({
    url: `/v1/call/script/toggle-status/${id}`,
    method: 'post',
    data
  })
}
// 更新话术分类
export function updateCategoryApi(id, data) {
  return request({
    url: `/v1/call/script/category/update/${id}`,
    method: 'put',
    data
  })
}
// 删除话术分类
export function deleteCategoryApi(id) {
  return request({
    url: `/v1/call/script/category/delete/${id}`,
    method: 'delete'
  })
}
// 获取分类列表（别名）
export function getCategoryListApi() {
  return getScriptCategoryListApi()
}
// 创建分类（别名）
export function createCategoryApi(data) {
  return createScriptCategoryApi(data)
}
