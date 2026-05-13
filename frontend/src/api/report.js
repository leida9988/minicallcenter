import request from '@/utils/request'
// 获取首页看板数据
export function getDashboardStatsApi() {
  return request({
    url: '/v1/report/dashboard',
    method: 'get'
  })
}
// 获取通话趋势统计
export function getCallTrendApi(params) {
  return request({
    url: '/v1/report/call/trend',
    method: 'get',
    params
  })
}
// 获取坐席绩效统计
export function getAgentPerformanceApi(params) {
  return request({
    url: '/v1/report/agent/performance',
    method: 'get',
    params
  })
}
// 获取客户分析统计
export function getCustomerAnalysisApi(params) {
  return request({
    url: '/v1/report/customer/analysis',
    method: 'get',
    params
  })
}
// 获取通话时段分布统计
export function getCallHourlyDistributionApi(params) {
  return request({
    url: '/v1/report/call/hourly-distribution',
    method: 'get',
    params
  })
}
// 获取操作日志列表
export function getOperationLogsApi(params) {
  return request({
    url: '/v1/report/operation/logs',
    method: 'get',
    params
  })
}
// 导出通话趋势报表
export function exportCallTrendApi(params) {
  return request({
    url: '/v1/report/export/call-trend',
    method: 'post',
    params,
    responseType: 'blob'
  })
}
// 导出坐席绩效报表
export function exportAgentPerformanceApi(params) {
  return request({
    url: '/v1/report/export/agent-performance',
    method: 'post',
    params,
    responseType: 'blob'
  })
}
// 导出客户分析报表
export function exportCustomerAnalysisApi(params) {
  return request({
    url: '/v1/report/export/customer-analysis',
    method: 'post',
    params,
    responseType: 'blob'
  })
}
