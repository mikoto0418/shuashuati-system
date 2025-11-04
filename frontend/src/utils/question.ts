export const QUESTION_TYPE_LABELS: Record<string, string> = {
  single_choice: '单选题',
  multiple_choice: '多选题',
  true_false: '判断题',
  fill_blank: '填空题',
  short_answer: '简答题'
};

export const QUESTION_TYPE_OPTIONS = [
  { label: QUESTION_TYPE_LABELS.single_choice, value: 'single_choice' },
  { label: QUESTION_TYPE_LABELS.multiple_choice, value: 'multiple_choice' },
  { label: QUESTION_TYPE_LABELS.true_false, value: 'true_false' },
  { label: QUESTION_TYPE_LABELS.fill_blank, value: 'fill_blank' },
  { label: QUESTION_TYPE_LABELS.short_answer, value: 'short_answer' }
];

export type QuestionTypeValue = keyof typeof QUESTION_TYPE_LABELS;

export function questionTypeLabel(
  type?: string | null,
  fallback: string = '未知题型'
): string {
  if (!type) return fallback;
  return QUESTION_TYPE_LABELS[type] ?? type;
}
