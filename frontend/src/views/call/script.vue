<template>
  <div class="script-container">
    <!-- 搜索区域 -->
    <div class="common-card">
      <el-form :model="queryParams" ref="queryFormRef" :inline="true" label-width="80px">
        <el-form-item label="话术名称" prop="keyword">
          <el-input
            v-model="queryParams.keyword"
            placeholder="请输入话术名称/关键词"
            clearable
            style="width: 250px"
          />
        </el-form-item>
        <el-form-item label="分类" prop="category_id">
          <el-select
            v-model="queryParams.category_id"
            placeholder="请选择分类"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="category in categoryList"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select
            v-model="queryParams.status"
            placeholder="请选择状态"
            clearable
            style="width: 120px"
          >
            <el-option label="全部" :value="null" />
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetQuery">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 操作按钮 -->
    <div class="common-card">
      <el-row :gutter="10">
        <el-col :span="24">
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新增话术
          </el-button>
          <el-button type="success" @click="handleCategoryManage">
            <el-icon><List /></el-icon>
            分类管理
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 表格区域 -->
    <div class="common-card">
      <el-table
        v-loading="loading"
        :data="scriptList"
        border
        stripe
      >
        <el-table-column prop="name" label="话术名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="category_name" label="分类" width="120" />
        <el-table-column prop="content" label="话术内容" min-width="300" show-overflow-tooltip />
        <el-table-column prop="use_count" label="使用次数" width="100" align="center" />
        <el-table-column prop="success_rate" label="成功率" width="100" align="center">
          <template #default="scope">
            {{ scope.row.success_rate ? `${scope.row.success_rate}%` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'" size="small">
              {{ scope.row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="update_user_name" label="更新人" width="100" />
        <el-table-column prop="updated_at" label="更新时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"
              text
              size="small"
              @click="viewDetail(scope.row)"
            >
              预览
            </el-button>
            <el-button
              type="warning"
              text
              size="small"
              @click="handleEdit(scope.row)"
            >
              编辑
            </el-button>
            <el-button
              type="success"
              text
              size="small"
              @click="toggleStatus(scope.row)"
            >
              {{ scope.row.status === 1 ? '禁用' : '启用' }}
            </el-button>
            <el-button
              type="danger"
              text
              size="small"
              @click="handleDelete(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.page_size"
          :total="total"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleQuery"
          @current-change="handleQuery"
        />
      </div>
    </div>

    <!-- 新增/编辑话术对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      destroy-on-close
    >
      <el-form :model="scriptForm" ref="scriptFormRef" label-width="100px" :rules="rules">
        <el-form-item label="话术名称" prop="name">
          <el-input v-model="scriptForm.name" placeholder="请输入话术名称" />
        </el-form-item>
        <el-form-item label="分类" prop="category_id">
          <el-select
            v-model="scriptForm.category_id"
            placeholder="请选择分类"
            style="width: 100%"
          >
            <el-option
              v-for="category in categoryList"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="话术内容" prop="content">
          <el-input
            v-model="scriptForm.content"
            type="textarea"
            :rows="10"
            placeholder="请输入话术内容，支持变量替换，例如：{{客户姓名}}、{{产品名称}}"
          />
          <div class="tip">
            支持的变量：{{客户姓名}}、{{客户公司}}、{{产品名称}}、{{产品价格}}、{{坐席姓名}}
          </div>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="scriptForm.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="2">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="话术描述">
          <el-input
            v-model="scriptForm.description"
            type="textarea"
            :rows="2"
            placeholder="请输入话术的使用场景和说明"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveScript" :loading="saveLoading">保存</el-button>
      </template>
    </el-dialog>

    <!-- 话术预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="话术预览"
      width="700px"
    >
      <div v-if="currentScript" class="preview-content">
        <div class="preview-header">
          <h3>{{ currentScript.name }}</h3>
          <el-tag :type="currentScript.status === 1 ? 'success' : 'danger'" size="small">
            {{ currentScript.status === 1 ? '启用' : '禁用' }}
          </el-tag>
        </div>
        <div class="preview-meta">
          <span>分类：{{ currentScript.category_name }}</span>
          <span>使用次数：{{ currentScript.use_count }} 次</span>
          <span>成功率：{{ currentScript.success_rate ? `${currentScript.success_rate}%` : '-' }}</span>
        </div>
        <div class="preview-body">
          <h4>话术内容：</h4>
          <div class="content-box">
            {{ currentScript.content }}
          </div>
        </div>
        <div class="preview-body" v-if="currentScript.description">
          <h4>使用说明：</h4>
          <div class="content-box">
            {{ currentScript.description }}
          </div>
        </div>
        <div class="preview-footer">
          <h4>变量替换示例：</h4>
          <div class="example-box">
            {{ replaceVariables(currentScript.content) }}
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="previewDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleEdit(currentScript)">编辑</el-button>
      </template>
    </el-dialog>

    <!-- 分类管理对话框 -->
    <el-dialog
      v-model="categoryDialogVisible"
      title="分类管理"
      width="500px"
    >
      <div class="category-manage">
        <el-form :inline="true" class="category-form">
          <el-form-item label="分类名称">
            <el-input v-model="newCategoryName" placeholder="请输入分类名称" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="addCategory" :loading="categoryLoading">
              <el-icon><Plus /></el-icon>
              添加
            </el-button>
          </el-form-item>
        </el-form>

        <el-table :data="categoryList" border stripe>
          <el-table-column prop="name" label="分类名称" />
          <el-table-column prop="script_count" label="话术数量" width="100" align="center" />
          <el-table-column prop="created_at" label="创建时间" width="160" />
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="scope">
              <el-button
                type="warning"
                text
                size="small"
                @click="editCategory(scope.row)"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                text
                size="small"
                @click="deleteCategory(scope.row)"
                :disabled="scope.row.script_count > 0"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, List } from '@element-plus/icons-vue'
import {
  getScriptListApi,
  createScriptApi,
  updateScriptApi,
  deleteScriptApi,
  toggleScriptStatusApi,
  getCategoryListApi,
  createCategoryApi,
  updateCategoryApi,
  deleteCategoryApi
} from '@/api/call'

const loading = ref(false)
const queryFormRef = ref(null)
const scriptFormRef = ref(null)
const scriptList = ref([])
const categoryList = ref([])
const total = ref(0)
const dialogVisible = ref(false)
const previewDialogVisible = ref(false)
const categoryDialogVisible = ref(false)
const currentScript = ref(null)
const saveLoading = ref(false)
const categoryLoading = ref(false)
const newCategoryName = ref('')
const editingCategory = ref(null)

// 查询参数
const queryParams = reactive({
  page: 1,
  page_size: 20,
  keyword: '',
  category_id: null,
  status: null
})

// 表单初始值
const initScriptForm = {
  name: '',
  category_id: null,
  content: '',
  status: 1,
  description: ''
}

const scriptForm = reactive({ ...initScriptForm })

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入话术名称', trigger: 'blur' },
    { min: 2, max: 50, message: '话术名称长度在 2 到 50 个字符之间', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入话术内容', trigger: 'blur' }
  ]
}

const dialogTitle = computed(() => currentScript.value ? '编辑话术' : '新增话术')

// 获取话术列表
const getScriptList = async () => {
  loading.value = true
  try {
    const res = await getScriptListApi(queryParams)
    scriptList.value = res.data.list
    total.value = res.data.total
  } catch (error) {
    ElMessage.error(error.message || '获取话术列表失败')
  } finally {
    loading.value = false
  }
}

// 获取分类列表
const getCategoryList = async () => {
  try {
    const res = await getCategoryListApi()
    categoryList.value = res.data.list
  } catch (error) {
    ElMessage.error('获取分类列表失败')
  }
}

// 搜索
const handleQuery = () => {
  queryParams.page = 1
  getScriptList()
}

// 重置
const resetQuery = () => {
  queryFormRef.value?.resetFields()
  handleQuery()
}

// 新增话术
const handleCreate = () => {
  currentScript.value = null
  Object.assign(scriptForm, initScriptForm)
  dialogVisible.value = true
}

// 编辑话术
const handleEdit = (row) => {
  currentScript.value = row
  Object.assign(scriptForm, {
    name: row.name,
    category_id: row.category_id,
    content: row.content,
    status: row.status,
    description: row.description
  })
  dialogVisible.value = true
}

// 保存话术
const saveScript = async () => {
  if (!scriptFormRef.value) return

  await scriptFormRef.value.validate(async (valid) => {
    if (!valid) return

    saveLoading.value = true
    try {
      if (currentScript.value) {
        await updateScriptApi(currentScript.value.id, scriptForm)
        ElMessage.success('话术更新成功')
      } else {
        await createScriptApi(scriptForm)
        ElMessage.success('话术创建成功')
      }

      dialogVisible.value = false
      getScriptList()
    } catch (error) {
      ElMessage.error(error.message || '保存失败')
    } finally {
      saveLoading.value = false
    }
  })
}

// 切换状态
const toggleStatus = async (row) => {
  try {
    const action = row.status === 1 ? '禁用' : '启用'
    await ElMessageBox.confirm(
      `确定要${action}话术 "${row.name}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await toggleScriptStatusApi(row.id, { status: row.status === 1 ? 2 : 1 })
    ElMessage.success(`话术已${action}`)
    getScriptList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败')
    }
  }
}

// 删除话术
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除话术 "${row.name}" 吗？删除后无法恢复。`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteScriptApi(row.id)
    ElMessage.success('话术删除成功')
    getScriptList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 查看详情
const viewDetail = (row) => {
  currentScript.value = row
  previewDialogVisible.value = true
}

// 替换变量示例
const replaceVariables = (content) => {
  return content
    .replace(/{{客户姓名}}/g, '张三')
    .replace(/{{客户公司}}/g, '某某科技有限公司')
    .replace(/{{产品名称}}/g, '智能呼叫系统')
    .replace(/{{产品价格}}/g, '998元/年')
    .replace(/{{坐席姓名}}/g, '李四')
}

// 分类管理
const handleCategoryManage = () => {
  newCategoryName.value = ''
  editingCategory.value = null
  categoryDialogVisible.value = true
}

// 添加分类
const addCategory = async () => {
  if (!newCategoryName.value.trim()) {
    ElMessage.warning('请输入分类名称')
    return
  }

  categoryLoading.value = true
  try {
    if (editingCategory.value) {
      await updateCategoryApi(editingCategory.value.id, { name: newCategoryName.value })
      ElMessage.success('分类更新成功')
    } else {
      await createCategoryApi({ name: newCategoryName.value })
      ElMessage.success('分类添加成功')
    }

    newCategoryName.value = ''
    editingCategory.value = null
    getCategoryList()
    getScriptList()
  } catch (error) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    categoryLoading.value = false
  }
}

// 编辑分类
const editCategory = (row) => {
  editingCategory.value = row
  newCategoryName.value = row.name
}

// 删除分类
const deleteCategory = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除分类 "${row.name}" 吗？删除后无法恢复。`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteCategoryApi(row.id)
    ElMessage.success('分类删除成功')
    getCategoryList()
    getScriptList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

onMounted(() => {
  getScriptList()
  getCategoryList()
})
</script>

<style lang="scss" scoped>
.script-container {
  .tip {
    font-size: 12px;
    color: #909399;
    margin-top: 5px;
  }

  .preview-content {
    .preview-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 15px;

      h3 {
        margin: 0;
        font-size: 20px;
        font-weight: bold;
      }
    }

    .preview-meta {
      display: flex;
      gap: 30px;
      margin-bottom: 20px;
      color: #909399;
      font-size: 14px;
    }

    .preview-body {
      margin-bottom: 20px;

      h4 {
        margin-bottom: 10px;
        font-size: 16px;
        font-weight: bold;
      }

      .content-box {
        padding: 15px;
        background: #f5f7fa;
        border-radius: 4px;
        line-height: 1.8;
        white-space: pre-wrap;
      }
    }

    .preview-footer {
      h4 {
        margin-bottom: 10px;
        font-size: 16px;
        font-weight: bold;
      }

      .example-box {
        padding: 15px;
        background: #ecf5ff;
        border-radius: 4px;
        line-height: 1.8;
        color: #409eff;
        white-space: pre-wrap;
      }
    }
  }

  .category-manage {
    .category-form {
      margin-bottom: 20px;
    }
  }
}
</style>
