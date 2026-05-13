<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="100px"
  >
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="客户姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入客户姓名" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="手机号码" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号码" />
        </el-form-item>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="性别">
          <el-radio-group v-model="form.gender">
            <el-radio :value="1">男</el-radio>
            <el-radio :value="2">女</el-radio>
            <el-radio :value="0">未知</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="年龄">
          <el-input-number
            v-model="form.age"
            :min="0"
            :max="150"
            placeholder="请输入年龄"
            style="width: 100%"
          />
        </el-form-item>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="电子邮箱">
          <el-input v-model="form.email" placeholder="请输入电子邮箱" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="公司名称">
          <el-input v-model="form.company" placeholder="请输入公司名称" />
        </el-form-item>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="职位">
          <el-input v-model="form.position" placeholder="请输入职位" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="客户来源">
          <el-input v-model="form.source" placeholder="请输入客户来源" />
        </el-form-item>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="客户等级">
          <el-select v-model="form.level" placeholder="请选择客户等级" style="width: 100%">
            <el-option label="普通" :value="1" />
            <el-option label="VIP" :value="2" />
            <el-option label="重要客户" :value="3" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="客户状态">
          <el-select v-model="form.status" placeholder="请选择客户状态" style="width: 100%">
            <el-option label="待联系" :value="1" />
            <el-option label="联系中" :value="2" />
            <el-option label="有意向" :value="3" />
            <el-option label="已成交" :value="4" />
            <el-option label="已拒绝" :value="5" />
            <el-option label="无效客户" :value="6" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="联系地址">
          <el-input v-model="form.address" placeholder="请输入联系地址" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="客户标签">
          <el-select
            v-model="form.tags"
            multiple
            placeholder="请选择客户标签"
            style="width: 100%"
            allow-create
            default-first-option
          >
            <el-option
              v-for="tag in tagList"
              :key="tag.id"
              :label="tag.name"
              :value="tag.name"
              :style="{ color: tag.color }"
            />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="24">
        <el-form-item label="客户描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入客户描述"
          />
        </el-form-item>
      </el-col>
    </el-row>
    <el-row :gutter="20">
      <el-col :span="24">
        <el-form-item label="备注">
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="2"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-col>
    </el-row>
    <el-row :gutter="20" v-if="showAssign">
      <el-col :span="12">
        <el-form-item label="分配坐席">
          <el-select
            v-model="form.assign_user_id"
            placeholder="请选择分配的坐席"
            style="width: 100%"
          >
            <el-option
              v-for="user in userList"
              :key="user.id"
              :label="user.nickname || user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="下次跟进时间">
          <el-date-picker
            v-model="form.next_follow_time"
            type="datetime"
            placeholder="请选择下次跟进时间"
            style="width: 100%"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
      </el-col>
    </el-row>
    <div class="dialog-footer">
      <el-button @click="$emit('close')">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="loading">确定</el-button>
    </div>
  </el-form>
</template>
<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/modules/user'
import { createCustomerApi, updateCustomerApi, getCustomerDetailApi } from '@/api/customer'
import { getUserListApi } from '@/api/user'
const userStore = useUserStore()
const emit = defineEmits(['success', 'close'])
const props = defineProps({
  customerId: {
    type: Number,
    default: null
  }
})
const formRef = ref(null)
const loading = ref(false)
const userList = ref([])
const tagList = ref([])
// 表单初始值
const initForm = {
  name: '',
  phone: '',
  gender: 0,
  age: null,
  email: '',
  company: '',
  position: '',
  source: '',
  address: '',
  level: 1,
  status: 1,
  tags: [],
  description: '',
  remark: '',
  assign_user_id: null,
  next_follow_time: ''
}
const form = reactive({ ...initForm })
// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入客户姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度在2到20个字符之间', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    { pattern: /^1[3456789]\d{9}$/, message: '手机号码格式不正确', trigger: 'blur' }
  ]
}
// 是否显示分配坐席选项（超级管理员可以分配）
const showAssign = computed(() => userStore.isSuperUser)
// 获取用户列表
const getUserList = async () => {
  if (!showAssign.value) return
  try {
    const res = await getUserListApi({ page: 1, page_size: 1000 })
    userList.value = res.data.list
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  }
}
// 获取客户详情
const getCustomerDetail = async (id) => {
  try {
    const res = await getCustomerDetailApi(id)
    Object.assign(form, res.data)
  } catch (error) {
    ElMessage.error('获取客户详情失败')
  }
}
// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        if (props.customerId) {
          await updateCustomerApi(props.customerId, form)
          ElMessage.success('修改客户成功')
        } else {
          await createCustomerApi(form)
          ElMessage.success('新增客户成功')
        }
        emit('success')
        emit('close')
      } catch (error) {
        ElMessage.error(error.message || '保存失败')
      } finally {
        loading.value = false
      }
    }
  })
}
watch(() => props.customerId, (newVal) => {
  if (newVal) {
    getCustomerDetail(newVal)
  } else {
    Object.assign(form, initForm)
  }
})
onMounted(() => {
  getUserList()
  if (props.customerId) {
    getCustomerDetail(props.customerId)
  }
})
</script>
<style lang="scss" scoped>
.dialog-footer {
  text-align: right;
  margin-top: 20px;
}
</style>
