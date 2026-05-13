import dayjs from 'dayjs'
// 格式化日期
export function formatDate(date, format = 'YYYY-MM-DD') {
  if (!date) return ''
  return dayjs(date).format(format)
}
// 格式化时间
export function formatTime(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!date) return ''
  return dayjs(date).format(format)
}
// 格式化时长（秒转时分秒）
export function formatDuration(seconds) {
  if (!seconds || seconds < 0) return '00:00:00'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}
// 获取今天开始时间
export function getTodayStart() {
  return dayjs().startOf('day').format('YYYY-MM-DD HH:mm:ss')
}
// 获取今天结束时间
export function getTodayEnd() {
  return dayjs().endOf('day').format('YYYY-MM-DD HH:mm:ss')
}
// 获取本周开始时间
export function getWeekStart() {
  return dayjs().startOf('week').format('YYYY-MM-DD HH:mm:ss')
}
// 获取本周结束时间
export function getWeekEnd() {
  return dayjs().endOf('week').format('YYYY-MM-DD HH:mm:ss')
}
// 获取本月开始时间
export function getMonthStart() {
  return dayjs().startOf('month').format('YYYY-MM-DD HH:mm:ss')
}
// 获取本月结束时间
export function getMonthEnd() {
  return dayjs().endOf('month').format('YYYY-MM-DD HH:mm:ss')
}
