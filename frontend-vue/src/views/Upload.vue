<template>
  <div class="upload-container">
    <!-- 上传区域 -->
    <div class="upload-section">
      <el-card class="upload-card">
        <template #header>
          <div class="card-header">
            <span>文档上传</span>
            <el-button type="text" @click="showUploadHelp = true">
              <el-icon><QuestionFilled /></el-icon>
            </el-button>
          </div>
        </template>
        
        <el-upload
          ref="uploadRef"
          class="upload-dragger"
          drag
          :action="uploadUrl"
          :headers="uploadHeaders"
          :multiple="true"
          :file-list="fileList"
          :before-upload="beforeUpload"
          :on-progress="onProgress"
          :on-success="onSuccess"
          :on-error="onError"
          :on-remove="onRemove"
          :accept="'.doc,.docx,.pdf,.txt'"
          :auto-upload="false"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 .doc, .docx, .pdf, .txt 格式，单个文件不超过 10MB
            </div>
          </template>
        </el-upload>
        
        <div class="upload-actions" v-if="fileList.length > 0">
          <el-button type="primary" @click="submitUpload" :loading="uploading">
            开始上传
          </el-button>
          <el-button @click="clearFiles">清空列表</el-button>
        </div>
      </el-card>
    </div>

    <!-- 上传历史 -->
    <div class="history-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>上传历史</span>
            <el-button type="text" @click="refreshHistory">
              <el-icon><Refresh /></el-icon>
            </el-button>
          </div>
        </template>
        
        <el-table 
          :data="historyList" 
          v-loading="historyLoading"
          empty-text="暂无上传记录"
        >
          <el-table-column prop="original_filename" label="文件名" min-width="200">
            <template #default="{ row }">
              <div class="filename-cell">
                <el-icon class="file-icon"><Document /></el-icon>
                <span class="filename">{{ row.original_filename || row.file_name || '未知文件' }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="file_size" label="文件大小" width="100">
            <template #default="{ row }">
              {{ formatFileSize(row.file_size) }}
            </template>
          </el-table-column>
          
          <el-table-column prop="status" label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="extracted_count" label="题目数量" width="100">
            <template #default="{ row }">
              {{ row.extracted_count || 0 }}
            </template>
          </el-table-column>
          
          <el-table-column prop="uploaded_at" label="上传时间" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.uploaded_at) }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button 
                type="text" 
                size="small" 
                @click="viewQuestions(row)"
                :disabled="row.status !== 'completed' || !row.extracted_count"
              >
                查看题目
              </el-button>
              <el-button 
                type="text" 
                size="small" 
                @click="reprocessFile(row)"
                :disabled="row.status === 'processing'"
              >
                重新处理
              </el-button>
              <el-button 
                type="text" 
                size="small" 
                @click="deleteRecord(row)"
                class="delete-btn"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <div class="pagination-wrapper" v-if="pagination.total > 0">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.per_page"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 上传帮助对话框 -->
    <el-dialog v-model="showUploadHelp" title="上传帮助" width="600px">
      <div class="help-content">
        <h4>支持的文件格式：</h4>
        <ul>
          <li><strong>.doc/.docx</strong> - Microsoft Word 文档</li>
          <li><strong>.pdf</strong> - PDF 文档</li>
          <li><strong>.txt</strong> - 纯文本文件</li>
        </ul>
        
        <h4>文件要求：</h4>
        <ul>
          <li>单个文件大小不超过 10MB</li>
          <li>文件内容应包含题目和答案</li>
          <li>建议使用清晰的格式排版</li>
        </ul>
        
        <h4>处理流程：</h4>
        <ol>
          <li>上传文件到服务器</li>
          <li>AI 解析文档内容</li>
          <li>提取题目和答案</li>
          <li>保存到题库中</li>
        </ol>
      </div>
    </el-dialog>

    <!-- 进度对话框 -->
    <el-dialog 
      v-model="showProgress" 
      title="处理进度" 
      width="500px" 
      :close-on-click-modal="false"
      :close-on-press-escape="false"
    >
      <div class="progress-content" v-if="currentProgress">
        <div class="progress-info">
          <p><strong>文件：</strong>{{ currentProgress.original_filename || currentProgress.file_name || '未知文件' }}</p>
          <p><strong>状态：</strong>{{ currentProgress.status }}</p>
          <p v-if="currentProgress.message"><strong>信息：</strong>{{ currentProgress.message }}</p>
        </div>
        
        <el-progress 
          :percentage="currentProgress.progress" 
          :status="currentProgress.status === 'failed' ? 'exception' : 'success'"
        />
      </div>
      
      <template #footer>
        <el-button @click="showProgress = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, type UploadInstance, type UploadProps, type UploadRawFile } from 'element-plus'
import { Document, UploadFilled, QuestionFilled, Refresh } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import type { ParsedDocument, PaginatedResponse } from '@/types/common'
import { useRouter } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()

// 上传相关
const uploadRef = ref<UploadInstance>()
const fileList = ref<any[]>([])
const uploading = ref(false)
const showUploadHelp = ref(false)

// 历史记录相关
const historyList = ref<ParsedDocument[]>([])
const historyLoading = ref(false)
const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0
})

// 进度相关
const showProgress = ref(false)
const currentProgress = ref<any>(null)

// 上传配置
const uploadUrl = computed(() => {
  return `${import.meta.env.VITE_API_BASE_URL}/api/upload`
})

const uploadHeaders = computed(() => {
  return {
    'Authorization': `Bearer ${authStore.token}`
  }
})

// 文件上传前检查
const beforeUpload: UploadProps['beforeUpload'] = (rawFile: UploadRawFile) => {
  const allowedTypes = ['.doc', '.docx', '.pdf', '.txt']
  const fileExtension = '.' + rawFile.name.split('.').pop()?.toLowerCase()
  
  if (!allowedTypes.includes(fileExtension)) {
    ElMessage.error('只支持 .doc, .docx, .pdf, .txt 格式的文件')
    return false
  }
  
  if (rawFile.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }
  
  return true
}

// 上传进度
const onProgress: UploadProps['onProgress'] = (evt, file) => {
  console.log('Upload progress:', evt.percent, file)
}

// 上传成功
const onSuccess: UploadProps['onSuccess'] = (response, file) => {
  console.log('Upload success:', response, file)
  if (response.success) {
    ElMessage.success('文件上传成功，开始处理...')
    // 开始监控处理进度
    startProgressMonitoring(response.data.file_id, file.name)
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

// 上传失败
const onError: UploadProps['onError'] = (error, file) => {
  console.error('Upload error:', error, file)
  ElMessage.error('文件上传失败')
  uploading.value = false
}

// 移除文件
const onRemove: UploadProps['onRemove'] = (file) => {
  console.log('Remove file:', file)
}

// 开始上传
const submitUpload = () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择要上传的文件')
    return
  }
  
  uploading.value = true
  uploadRef.value?.submit()
}

// 清空文件列表
const clearFiles = () => {
  uploadRef.value?.clearFiles()
  fileList.value = []
}

// 开始进度监控
const startProgressMonitoring = (fileId: string, fileName: string) => {
  currentProgress.value = {
    file_id: fileId,
    original_filename: fileName,
    progress: 0,
    status: 'processing',
    message: '开始处理...'
  }
  showProgress.value = true
  
  // 轮询检查进度
  const checkProgress = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/upload/status/${fileId}`, {
        headers: {
          'Authorization': `Bearer ${authStore.token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          currentProgress.value = {
            ...currentProgress.value,
            ...data.data,
            progress: data.data.progress || 0
          }
          
          if (data.data.status === 'completed' || data.data.status === 'failed') {
            uploading.value = false
            if (data.data.status === 'completed') {
              ElMessage.success('文件处理完成！')
              refreshHistory() // 刷新历史记录
            } else {
              ElMessage.error(data.data.error_message || '文件处理失败')
            }
            setTimeout(() => {
              showProgress.value = false
            }, 2000)
          } else {
            // 继续轮询
            setTimeout(checkProgress, 2000)
          }
        }
      }
    } catch (error) {
      console.error('Check progress error:', error)
      uploading.value = false
    }
  }
  
  // 开始检查
  setTimeout(checkProgress, 1000)
}

// 获取上传历史
const getUploadHistory = async () => {
  historyLoading.value = true
  try {
    const response = await fetch(
      `${import.meta.env.VITE_API_BASE_URL}/api/upload/history?page=${pagination.page}&per_page=${pagination.per_page}`,
      {
        headers: {
          'Authorization': `Bearer ${authStore.token}`
        }
      }
    )
    
    if (response.ok) {
      const data: { success: boolean; data: PaginatedResponse<ParsedDocument> } = await response.json()
      if (data.success) {
        historyList.value = data.data.items
        pagination.total = data.data.total
      }
    }
  } catch (error) {
    console.error('Get upload history error:', error)
    ElMessage.error('获取上传历史失败')
  } finally {
    historyLoading.value = false
  }
}

// 刷新历史记录
const refreshHistory = () => {
  getUploadHistory()
}

// 分页处理
const handleSizeChange = (val: number) => {
  pagination.per_page = val
  pagination.page = 1
  getUploadHistory()
}

const handleCurrentChange = (val: number) => {
  pagination.page = val
  getUploadHistory()
}

// 查看题目
const viewQuestions = (record: ParsedDocument) => {
  router.push({
    name: 'QuestionList',
    query: {
      file_id: record.file_id
    }
  })
}

// 重新处理文件
const reprocessFile = async (record: ParsedDocument) => {
  try {
    await ElMessageBox.confirm(
      `确定要重新处理文件 "${record.original_filename || record.file_name || '未知文件'}" 吗？`,
      '确认重新处理',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await fetch(
      `${import.meta.env.VITE_API_BASE_URL}/api/upload/reprocess/${record.file_id}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authStore.token}`
        }
      }
    )
    
    if (response.ok) {
      const data = await response.json()
      if (data.success) {
        ElMessage.success('开始重新处理文件')
        // 开始监控进度
        startProgressMonitoring(record.file_id, record.original_filename || record.file_name || '未知文件')
        refreshHistory()
      } else {
        ElMessage.error(data.message || '重新处理失败')
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Reprocess file error:', error)
      ElMessage.error('重新处理失败')
    }
  }
}

// 删除记录
const deleteRecord = async (record: ParsedDocument) => {
  // 检查记录是否完整
  if (!record || (!record.original_filename && !record.file_name)) {
    ElMessage.error('记录信息不完整，无法删除')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除文件 "${record.original_filename || record.file_name || '未知文件'}" 及其相关数据吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await fetch(
      `${import.meta.env.VITE_API_BASE_URL}/api/upload/${record.file_id}`,
      {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${authStore.token}`
        }
      }
    )
    
    if (response.ok) {
      const data = await response.json()
      if (data.success) {
        ElMessage.success('删除成功')
        refreshHistory()
      } else {
        ElMessage.error(data.message || '删除失败')
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete record error:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 工具函数
const formatFileSize = (size: number) => {
  if (!size) return '-'
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB'
  return (size / (1024 * 1024)).toFixed(1) + ' MB'
}

const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'completed': return 'success'
    case 'processing': return 'warning'
    case 'failed': return 'danger'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'pending': return '等待处理'
    case 'processing': return '处理中'
    case 'completed': return '已完成'
    case 'failed': return '处理失败'
    default: return '未知状态'
  }
}

// 组件挂载时获取历史记录
onMounted(() => {
  getUploadHistory()
})
</script>

<style scoped>
.upload-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.upload-section {
  margin-bottom: 30px;
}

.upload-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-dragger {
  width: 100%;
}

.upload-actions {
  margin-top: 20px;
  text-align: center;
}

.upload-actions .el-button {
  margin: 0 10px;
}

.history-section .el-card {
  border-radius: 8px;
}

.filename-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  color: #409eff;
  font-size: 16px;
}

.filename {
  word-break: break-all;
}

.delete-btn {
  color: #f56c6c;
}

.delete-btn:hover {
  color: #f56c6c;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.help-content h4 {
  margin: 20px 0 10px 0;
  color: #303133;
}

.help-content ul,
.help-content ol {
  margin: 10px 0;
  padding-left: 20px;
}

.help-content li {
  margin: 5px 0;
  line-height: 1.6;
}

.progress-content {
  padding: 20px 0;
}

.progress-info {
  margin-bottom: 20px;
}

.progress-info p {
  margin: 8px 0;
  line-height: 1.6;
}
</style>
