<template>
  <div class="config-manage-container">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>系统配置</span>
        </div>
      </template>

      <el-tabs v-model="activeTab" type="card">
        <!-- 基础配置 -->
        <el-tab-pane label="基础配置" name="base">
          <el-form :model="baseConfig" ref="baseConfigForm" label-width="150px">
            <el-form-item label="系统名称">
              <el-input v-model="baseConfig.system_name" placeholder="请输入系统名称" />
            </el-form-item>
            <el-form-item label="系统Logo">
              <el-upload
                class="avatar-uploader"
                action="#"
                :show-file-list="false"
                :on-success="handleLogoUploadSuccess"
                :before-upload="beforeLogoUpload"
              >
                <img v-if="baseConfig.system_logo" :src="baseConfig.system_logo" class="avatar" />
                <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
              </el-upload>
            </el-form-item>
            <el-form-item label="系统副标题">
              <el-input v-model="baseConfig.system_subtitle" placeholder="请输入系统副标题" />
            </el-form-item>
            <el-form-item label="系统描述">
              <el-input
                v-model="baseConfig.system_description"
                type="textarea"
                :rows="3"
                placeholder="请输入系统描述"
              />
            </el-form-item>
            <el-form-item label="版权信息">
              <el-input v-model="baseConfig.copyright" placeholder="请输入版权信息" />
            </el-form-item>
            <el-form-item label="备案号">
              <el-input v-model="baseConfig.icp_number" placeholder="请输入备案号" />
            </el-form-item>
            <el-form-item label="默认首页">
              <el-select v-model="baseConfig.default_route" placeholder="请选择默认首页" style="width: 300px">
                <el-option label="首页" value="/dashboard" />
                <el-option label="客户管理" value="/customer" />
                <el-option label="呼叫中心" value="/call" />
                <el-option label="统计报表" value="/report" />
              </el-select>
            </el-form-item>
            <el-form-item label="登录页面背景">
              <el-upload
                action="#"
                list-type="picture-card"
                :show-file-list="false"
                :on-success="handleLoginBgUploadSuccess"
                :before-upload="beforeLogoUpload"
              >
                <img v-if="baseConfig.login_bg" :src="baseConfig.login_bg" class="bg-preview" />
                <el-icon v-else><Plus /></el-icon>
              </el-upload>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveBaseConfig" :loading="baseLoading">保存配置</el-button>
              <el-button @click="resetBaseConfig">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 呼叫配置 -->
        <el-tab-pane label="呼叫配置" name="call">
          <el-form :model="callConfig" ref="callConfigForm" label-width="150px">
            <el-form-item label="外呼号码池">
              <el-select
                v-model="callConfig.default_caller_id"
                placeholder="请选择默认外呼号码"
                style="width: 300px"
              >
                <el-option
                  v-for="number in callerNumberList"
                  :key="number.id"
                  :label="`${number.number} (${number.description})`"
                  :value="number.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="自动外呼并发数">
              <el-input-number v-model="callConfig.auto_call_concurrent" :min="1" :max="100" style="width: 120px" />
              <span class="ml-2 text-gray-500">同时进行的自动外呼任务数量</span>
            </el-form-item>
            <el-form-item label="呼叫超时时间">
              <el-input-number v-model="callConfig.call_timeout" :min="10" :max="60" style="width: 120px" />
              <span class="ml-2 text-gray-500">秒，呼叫无响应超时时间</span>
            </el-form-item>
            <el-form-item label="通话后自动弹屏">
              <el-switch v-model="callConfig.auto_popup" />
              <span class="ml-2 text-gray-500">通话结束后自动弹出客户信息和跟进页面</span>
            </el-form-item>
            <el-form-item label="自动录音">
              <el-switch v-model="callConfig.auto_record" />
              <span class="ml-2 text-gray-500">通话自动录音</span>
            </el-form-item>
            <el-form-item label="录音保存时长">
              <el-input-number v-model="callConfig.record_save_days" :min="7" :max="3650" style="width: 120px" />
              <span class="ml-2 text-gray-500">天，录音文件自动删除时间</span>
            </el-form-item>
            <el-form-item label="录音存储位置">
              <el-select v-model="callConfig.record_storage" placeholder="请选择存储位置" style="width: 300px">
                <el-option label="本地存储" value="local" />
                <el-option label="阿里云OSS" value="oss" />
                <el-option label="腾讯云COS" value="cos" />
                <el-option label="七牛云Kodo" value="qiniu" />
              </el-select>
            </el-form-item>
            <el-form-item label="外呼时段限制">
              <el-time-picker
                v-model="callConfig.call_time_range"
                is-range
                range-separator="至"
                start-placeholder="开始时间"
                end-placeholder="结束时间"
                style="width: 300px"
                format="HH:mm"
                value-format="HH:mm"
              />
              <span class="ml-2 text-gray-500">只能在此时间段内进行外呼</span>
            </el-form-item>
            <el-form-item label="节假日禁止外呼">
              <el-switch v-model="callConfig.holiday_forbidden" />
              <span class="ml-2 text-gray-500">节假日不允许外呼</span>
            </el-form-item>
            <el-form-item label="重复呼叫间隔">
              <el-input-number v-model="callConfig.repeat_call_interval" :min="0" :max="10080" style="width: 120px" />
              <span class="ml-2 text-gray-500">分钟，同一客户两次呼叫的最小间隔，0表示不限制</span>
            </el-form-item>
            <el-form-item label="客户呼叫上限">
              <el-input-number v-model="callConfig.max_call_per_customer" :min="0" :max="100" style="width: 120px" />
              <span class="ml-2 text-gray-500">次/天，同一客户每天最大呼叫次数，0表示不限制</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveCallConfig" :loading="callLoading">保存配置</el-button>
              <el-button @click="resetCallConfig">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 安全配置 -->
        <el-tab-pane label="安全配置" name="security">
          <el-form :model="securityConfig" ref="securityConfigForm" label-width="150px">
            <el-form-item label="密码最小长度">
              <el-input-number v-model="securityConfig.password_min_length" :min="6" :max="20" style="width: 120px" />
            </el-form-item>
            <el-form-item label="密码复杂度要求">
              <el-checkbox-group v-model="securityConfig.password_complexity">
                <el-checkbox label="must_contain_letter">必须包含字母</el-checkbox>
                <el-checkbox label="must_contain_number">必须包含数字</el-checkbox>
                <el-checkbox label="must_contain_special_char">必须包含特殊字符</el-checkbox>
                <el-checkbox label="must_contain_upper_lower">必须包含大小写字母</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item label="密码有效期">
              <el-input-number v-model="securityConfig.password_expire_days" :min="0" :max="365" style="width: 120px" />
              <span class="ml-2 text-gray-500">天，0表示永不过期</span>
            </el-form-item>
            <el-form-item label="密码重复使用限制">
              <el-input-number v-model="securityConfig.password_history_limit" :min="0" :max="10" style="width: 120px" />
              <span class="ml-2 text-gray-500">次，不能使用最近N次使用过的密码，0表示不限制</span>
            </el-form-item>
            <el-form-item label="登录失败锁定">
              <el-row :gutter="20">
                <el-col :span="4">
                  <el-input-number v-model="securityConfig.login_fail_max_count" :min="0" :max="20" style="width: 100%" />
                </el-col>
                <el-col :span="20" class="flex items-center">
                  <span class="text-gray-500">次登录失败后锁定账号，0表示不锁定</span>
                </el-col>
              </el-row>
            </el-form-item>
            <el-form-item label="账号锁定时间">
              <el-input-number v-model="securityConfig.login_lock_minutes" :min="1" :max="1440" style="width: 120px" />
              <span class="ml-2 text-gray-500">分钟，账号被锁定的时长</span>
            </el-form-item>
            <el-form-item label="登录超时时间">
              <el-input-number v-model="securityConfig.session_expire_minutes" :min="15" :max="1440" style="width: 120px" />
              <span class="ml-2 text-gray-500">分钟，无操作自动登出时间</span>
            </el-form-item>
            <el-form-item label="允许多端登录">
              <el-switch v-model="securityConfig.allow_multi_device" />
              <span class="ml-2 text-gray-500">是否允许同一账号在多个设备同时登录</span>
            </el-form-item>
            <el-form-item label="IP白名单">
              <el-input
                v-model="securityConfig.ip_whitelist"
                type="textarea"
                :rows="3"
                placeholder="请输入允许访问的IP地址，多个用逗号分隔，支持CIDR格式"
              />
              <div class="text-gray-500 text-sm mt-1">留空表示不限制IP访问</div>
            </el-form-item>
            <el-form-item label="登录验证码">
              <el-switch v-model="securityConfig.login_captcha_enabled" />
              <span class="ml-2 text-gray-500">登录时需要输入验证码</span>
            </el-form-item>
            <el-form-item label="操作日志保留时长">
              <el-input-number v-model="securityConfig.operation_log_save_days" :min="7" :max="3650" style="width: 120px" />
              <span class="ml-2 text-gray-500">天，操作日志自动删除时间</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSecurityConfig" :loading="securityLoading">保存配置</el-button>
              <el-button @click="resetSecurityConfig">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 短信配置 -->
        <el-tab-pane label="短信配置" name="sms">
          <el-form :model="smsConfig" ref="smsConfigForm" label-width="150px">
            <el-form-item label="短信服务商">
              <el-select v-model="smsConfig.provider" placeholder="请选择短信服务商" style="width: 300px">
                <el-option label="阿里云短信" value="aliyun" />
                <el-option label="腾讯云短信" value="tencent" />
                <el-option label="百度云短信" value="baidu" />
                <el-option label="七牛云短信" value="qiniu" />
                <el-option label="自定义接口" value="custom" />
              </el-select>
            </el-form-item>
            <el-form-item label="AccessKey ID">
              <el-input v-model="smsConfig.access_key_id" placeholder="请输入AccessKey ID" />
            </el-form-item>
            <el-form-item label="AccessKey Secret">
              <el-input v-model="smsConfig.access_key_secret" type="password" placeholder="请输入AccessKey Secret" />
            </el-form-item>
            <el-form-item label="短信签名">
              <el-input v-model="smsConfig.sign_name" placeholder="请输入短信签名" />
            </el-form-item>
            <el-form-item label="验证码模板ID">
              <el-input v-model="smsConfig.captcha_template_id" placeholder="请输入验证码短信模板ID" />
            </el-form-item>
            <el-form-item label="通知模板ID">
              <el-input v-model="smsConfig.notify_template_id" placeholder="请输入通知短信模板ID" />
            </el-form-item>
            <el-form-item label="营销模板ID">
              <el-input v-model="smsConfig.marketing_template_id" placeholder="请输入营销短信模板ID" />
            </el-form-item>
            <el-form-item label="短信发送限制">
              <el-row :gutter="20">
                <el-col :span="4">
                  <el-input-number v-model="smsConfig.max_send_per_day" :min="0" :max="10000" style="width: 100%" />
                </el-col>
                <el-col :span="20" class="flex items-center">
                  <span class="text-gray-500">条/天，同一个手机号每天最多发送条数，0表示不限制</span>
                </el-col>
              </el-row>
            </el-form-item>
            <el-form-item label="短信发送间隔">
              <el-input-number v-model="smsConfig.send_interval_seconds" :min="60" :max="3600" style="width: 120px" />
              <span class="ml-2 text-gray-500">秒，同一个手机号两次发送的最小间隔</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSmsConfig" :loading="smsLoading">保存配置</el-button>
              <el-button @click="testSmsConfig" :loading="testLoading">测试配置</el-button>
              <el-button @click="resetSmsConfig">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 存储配置 -->
        <el-tab-pane label="存储配置" name="storage">
          <el-form :model="storageConfig" ref="storageConfigForm" label-width="150px">
            <el-form-item label="默认存储方式">
              <el-select v-model="storageConfig.default_storage" placeholder="请选择默认存储方式" style="width: 300px">
                <el-option label="本地存储" value="local" />
                <el-option label="阿里云OSS" value="oss" />
                <el-option label="腾讯云COS" value="cos" />
                <el-option label="七牛云Kodo" value="qiniu" />
              </el-select>
            </el-form-item>

            <el-divider content-position="left">阿里云OSS配置</el-divider>
            <el-form-item label="Endpoint">
              <el-input v-model="storageConfig.oss_endpoint" placeholder="请输入OSS Endpoint" />
            </el-form-item>
            <el-form-item label="AccessKey ID">
              <el-input v-model="storageConfig.oss_access_key_id" placeholder="请输入AccessKey ID" />
            </el-form-item>
            <el-form-item label="AccessKey Secret">
              <el-input v-model="storageConfig.oss_access_key_secret" type="password" placeholder="请输入AccessKey Secret" />
            </el-form-item>
            <el-form-item label="Bucket名称">
              <el-input v-model="storageConfig.oss_bucket" placeholder="请输入Bucket名称" />
            </el-form-item>
            <el-form-item label="自定义域名">
              <el-input v-model="storageConfig.oss_custom_domain" placeholder="请输入自定义域名，可选" />
            </el-form-item>

            <el-divider content-position="left">腾讯云COS配置</el-divider>
            <el-form-item label="Region">
              <el-input v-model="storageConfig.cos_region" placeholder="请输入COS Region" />
            </el-form-item>
            <el-form-item label="SecretId">
              <el-input v-model="storageConfig.cos_secret_id" placeholder="请输入SecretId" />
            </el-form-item>
            <el-form-item label="SecretKey">
              <el-input v-model="storageConfig.cos_secret_key" type="password" placeholder="请输入SecretKey" />
            </el-form-item>
            <el-form-item label="Bucket名称">
              <el-input v-model="storageConfig.cos_bucket" placeholder="请输入Bucket名称" />
            </el-form-item>
            <el-form-item label="自定义域名">
              <el-input v-model="storageConfig.cos_custom_domain" placeholder="请输入自定义域名，可选" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="saveStorageConfig" :loading="storageLoading">保存配置</el-button>
              <el-button @click="testStorageConfig" :loading="testStorageLoading">测试配置</el-button>
              <el-button @click="resetStorageConfig">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 测试短信对话框 -->
    <el-dialog
      v-model="testSmsDialogVisible"
      title="测试短信配置"
      width="500px"
    >
      <el-form :model="testSmsForm" label-width="100px">
        <el-form-item label="测试手机号">
          <el-input v-model="testSmsForm.mobile" placeholder="请输入接收测试短信的手机号" />
        </el-form-item>
        <el-form-item label="测试内容">
          <el-input type="textarea" v-model="testSmsForm.content" placeholder="请输入测试短信内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="testSmsDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="sendTestSms" :loading="testSending">发送测试短信</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElUpload } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const activeTab = ref('base')
const baseConfigForm = ref(null)
const callConfigForm = ref(null)
const securityConfigForm = ref(null)
const smsConfigForm = ref(null)
const storageConfigForm = ref(null)

const baseLoading = ref(false)
const callLoading = ref(false)
const securityLoading = ref(false)
const smsLoading = ref(false)
const storageLoading = ref(false)
const testLoading = ref(false)
const testStorageLoading = ref(false)

const testSmsDialogVisible = ref(false)
const testSending = ref(false)

// 外呼号码列表
const callerNumberList = ref([
  { id: 1, number: '13800138000', description: '客服1号线' },
  { id: 2, number: '13800138001', description: '客服2号线' },
  { id: 3, number: '13800138002', description: '营销1号线' }
])

// 基础配置
const baseConfig = reactive({
  system_name: '电话营销系统',
  system_logo: '',
  system_subtitle: '高效、智能的客户联系解决方案',
  system_description: '基于Vue3 + FastAPI + FreeSWITCH构建的全功能电话营销系统，支持客户管理、外呼中心、统计报表、AI集成等功能。',
  copyright: '© 2024 电话营销系统 版权所有',
  icp_number: '粤ICP备XXXXXXXX号-X',
  default_route: '/dashboard',
  login_bg: ''
})

// 呼叫配置
const callConfig = reactive({
  default_caller_id: 1,
  auto_call_concurrent: 10,
  call_timeout: 30,
  auto_popup: true,
  auto_record: true,
  record_save_days: 180,
  record_storage: 'local',
  call_time_range: ['09:00', '21:00'],
  holiday_forbidden: false,
  repeat_call_interval: 60,
  max_call_per_customer: 3
})

// 安全配置
const securityConfig = reactive({
  password_min_length: 8,
  password_complexity: ['must_contain_letter', 'must_contain_number'],
  password_expire_days: 90,
  password_history_limit: 3,
  login_fail_max_count: 5,
  login_lock_minutes: 30,
  session_expire_minutes: 120,
  allow_multi_device: false,
  ip_whitelist: '',
  login_captcha_enabled: true,
  operation_log_save_days: 180
})

// 短信配置
const smsConfig = reactive({
  provider: 'aliyun',
  access_key_id: '',
  access_key_secret: '',
  sign_name: '',
  captcha_template_id: '',
  notify_template_id: '',
  marketing_template_id: '',
  max_send_per_day: 10,
  send_interval_seconds: 60
})

// 存储配置
const storageConfig = reactive({
  default_storage: 'local',
  oss_endpoint: '',
  oss_access_key_id: '',
  oss_access_key_secret: '',
  oss_bucket: '',
  oss_custom_domain: '',
  cos_region: '',
  cos_secret_id: '',
  cos_secret_key: '',
  cos_bucket: '',
  cos_custom_domain: ''
})

// 测试短信表单
const testSmsForm = reactive({
  mobile: '',
  content: '这是一条测试短信，您的系统短信配置工作正常。'
})

// Logo上传前校验
const beforeLogoUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB')
    return false
  }
  return true
}

// Logo上传成功
const handleLogoUploadSuccess = (response, file) => {
  // 这里应该使用实际返回的URL
  baseConfig.system_logo = URL.createObjectURL(file.raw)
  ElMessage.success('Logo上传成功')
}

// 登录背景上传成功
const handleLoginBgUploadSuccess = (response, file) => {
  // 这里应该使用实际返回的URL
  baseConfig.login_bg = URL.createObjectURL(file.raw)
  ElMessage.success('背景图片上传成功')
}

// 保存基础配置
const saveBaseConfig = async () => {
  if (!baseConfigForm.value) return

  await baseConfigForm.value.validate(async (valid) => {
    if (!valid) return

    baseLoading.value = true
    try {
      // 这里调用API保存配置
      ElMessage.success('基础配置保存成功')
    } catch (error) {
      ElMessage.error(error.message || '保存失败')
    } finally {
      baseLoading.value = false
    }
  })
}

// 重置基础配置
const resetBaseConfig = () => {
  baseConfigForm.value?.resetFields()
}

// 保存呼叫配置
const saveCallConfig = async () => {
  if (!callConfigForm.value) return

  await callConfigForm.value.validate(async (valid) => {
    if (!valid) return

    callLoading.value = true
    try {
      // 这里调用API保存配置
      ElMessage.success('呼叫配置保存成功')
    } catch (error) {
      ElMessage.error(error.message || '保存失败')
    } finally {
      callLoading.value = false
    }
  })
}

// 重置呼叫配置
const resetCallConfig = () => {
  callConfigForm.value?.resetFields()
}

// 保存安全配置
const saveSecurityConfig = async () => {
  if (!securityConfigForm.value) return

  await securityConfigForm.value.validate(async (valid) => {
    if (!valid) return

    securityLoading.value = true
    try {
      // 这里调用API保存配置
      ElMessage.success('安全配置保存成功')
    } catch (error) {
      ElMessage.error(error.message || '保存失败')
    } finally {
      securityLoading.value = false
    }
  })
}

// 重置安全配置
const resetSecurityConfig = () => {
  securityConfigForm.value?.resetFields()
}

// 保存短信配置
const saveSmsConfig = async () => {
  if (!smsConfigForm.value) return

  await smsConfigForm.value.validate(async (valid) => {
    if (!valid) return

    smsLoading.value = true
    try {
      // 这里调用API保存配置
      ElMessage.success('短信配置保存成功')
    } catch (error) {
      ElMessage.error(error.message || '保存失败')
    } finally {
      smsLoading.value = false
    }
  })
}

// 测试短信配置
const testSmsConfig = () => {
  testSmsDialogVisible.value = true
}

// 发送测试短信
const sendTestSms = async () => {
  if (!testSmsForm.mobile) {
    ElMessage.error('请输入测试手机号')
    return
  }
  if (!testSmsForm.content) {
    ElMessage.error('请输入测试内容')
    return
  }

  testSending.value = true
  try {
    // 这里调用API发送测试短信
    ElMessage.success('测试短信发送成功，请查收')
    testSmsDialogVisible.value = false
  } catch (error) {
    ElMessage.error(error.message || '发送失败')
  } finally {
    testSending.value = false
  }
}

// 重置短信配置
const resetSmsConfig = () => {
  smsConfigForm.value?.resetFields()
}

// 保存存储配置
const saveStorageConfig = async () => {
  if (!storageConfigForm.value) return

  await storageConfigForm.value.validate(async (valid) => {
    if (!valid) return

    storageLoading.value = true
    try {
      // 这里调用API保存配置
      ElMessage.success('存储配置保存成功')
    } catch (error) {
      ElMessage.error(error.message || '保存失败')
    } finally {
      storageLoading.value = false
    }
  })
}

// 测试存储配置
const testStorageConfig = async () => {
  testStorageLoading.value = true
  try {
    // 这里调用API测试存储配置
    ElMessage.success('存储配置测试成功，连接正常')
  } catch (error) {
    ElMessage.error(error.message || '测试失败')
  } finally {
    testStorageLoading.value = false
  }
}

// 重置存储配置
const resetStorageConfig = () => {
  storageConfigForm.value?.resetFields()
}
</script>

<style lang="scss" scoped>
.config-manage-container {
  .config-card {
    :deep(.el-tabs__header) {
      margin: 0 -20px 20px -20px;
      padding: 0 20px;
    }
  }

  .avatar-uploader {
    :deep(.el-upload) {
      border: 1px dashed var(--el-border-color);
      border-radius: 6px;
      cursor: pointer;
      position: relative;
      overflow: hidden;
      transition: var(--el-transition-duration-fast);

      &:hover {
        border-color: var(--el-color-primary);
      }
    }

    .avatar-uploader-icon {
      font-size: 28px;
      color: #8c939d;
      width: 100px;
      height: 100px;
      text-align: center;
    }

    .avatar {
      width: 100px;
      height: 100px;
      display: block;
      object-fit: cover;
    }
  }

  .bg-preview {
    width: 200px;
    height: 120px;
    object-fit: cover;
  }
}
</style>
