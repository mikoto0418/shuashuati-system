// 通用类型定义
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface Category {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface UploadFile {
  id: string;
  filename: string;
  original_name: string;
  size: number;
  type: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
}

export interface UploadStatus {
  status: 'idle' | 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  message?: string;
  file_id?: string;
}

export interface UploadProgress {
  file_id: string;
  original_filename: string;
  file_name?: string; // 兼容旧字段
  progress: number;
  status: string;
  message?: string;
}

export interface ParsedQuestion {
  id: number;
  content: string;
  options?: string[];
  answer?: string;
  explanation?: string;
  difficulty?: string;
  type?: string;
  category_id?: number;
}

export interface ParseStatus {
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message?: string;
  questions_count?: number;
}

export interface ParsedDocument {
  id: number;
  file_id: string;
  original_filename: string; // 后端返回的主要字段
  file_name?: string; // 兼容旧字段
  file_size?: number;
  file_type?: string;
  content?: string;
  questions?: ParsedQuestion[];
  status: 'pending' | 'processing' | 'completed' | 'failed';
  extracted_count?: number;
  error_message?: string;
  created_at?: string;
  updated_at?: string;
  uploaded_at?: string;
  processed_at?: string;
  processing_started_at?: string;
  question_types?: string[];
  questions_preview?: ParsedQuestion[];
}

export interface FormRule {
  required?: boolean;
  message?: string;
  trigger?: string | string[];
  min?: number;
  max?: number;
  pattern?: RegExp;
  validator?: (rule: any, value: any, callback: any) => void;
}

export interface TableColumn {
  prop: string;
  label: string;
  width?: string | number;
  minWidth?: string | number;
  fixed?: boolean | 'left' | 'right';
  sortable?: boolean;
  formatter?: (row: any, column: any, cellValue: any, index: number) => string;
}

export interface Option {
  label: string;
  value: string | number;
  disabled?: boolean;
}

export interface Statistics {
  total_questions: number;
  total_documents: number;
  total_categories: number;
  recent_uploads: number;
}

export interface ActivityItem {
  id: number;
  type: 'upload' | 'parse' | 'practice' | 'system';
  title: string;
  description?: string;
  timestamp: string;
  status?: 'success' | 'warning' | 'error' | 'info';
}

export interface HealthStatus {
  status: 'healthy' | 'warning' | 'error';
  message?: string;
  details?: Record<string, any>;
}

export interface ProcessingLog {
  id: number;
  file_id: string;
  step: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  message?: string;
  details?: Record<string, any>;
  created_at: string;
  updated_at: string;
}
