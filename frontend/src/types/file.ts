export interface ParsedOption {
  key: string;
  content: string;
}

export interface ParsedQuestion {
  index: number;
  question: string;
  question_type: string;
  options: ParsedOption[];
  answer: string;
  explanation: string;
  raw_text: string;
  tags: string[];
}

export interface FilePreviewResponse {
  file_path: string;
  original_name: string;
  text: string;
  questions: ParsedQuestion[];
  mode: 'basic' | 'ai' | 'mixed';
  used_ai: boolean;
  warnings: string[];
  stats?: Record<string, any> | null;
  events: ParseTaskEvent[];
  auto_imported: boolean;
  import_summary?: Record<string, any> | null;
}

export interface FileImportRequest {
  file_path: string;
  category_id?: number | null;
  questions: ParsedQuestion[];
}

export interface FileImportResult {
  success_count: number;
  failed_count: number;
  created_ids: number[];
  errors: string[];
}

export interface ParseTaskCreateResponse {
  task_id: number;
  original_name: string;
  file_path: string;
}

export interface ParseTaskEvent {
  type: string;
  message: string;
  segment?: number;
  status?: string;
  elapsed?: number;
  timestamp?: string;
}

export interface ParseTaskStatus {
  id: number;
  status: string;
  progress: number;
  mode: 'basic' | 'ai' | 'mixed';
  original_name: string;
  file_path: string;
  warnings: string[];
  error?: string | null;
  stats?: Record<string, any> | null;
  events: ParseTaskEvent[];
  created_at: string;
  updated_at: string;
}

export interface ParseTaskResult {
  id: number;
  status: string;
  questions: ParsedQuestion[];
  warnings: string[];
  original_name: string;
  file_path: string;
  used_ai: boolean;
  stats?: Record<string, any> | null;
  events: ParseTaskEvent[];
  auto_imported: boolean;
  import_summary?: Record<string, any> | null;
}

export interface ParseTaskListResponse {
  tasks: ParseTaskStatus[];
}
