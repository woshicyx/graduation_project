// 自定义 React Hooks
// 在此导出项目使用的 hooks，例如：export { useDebounce } from './use-debounce';

// 解析 JSON 数组的辅助函数
export function parseJsonArray<T>(value: unknown): T[] {
  if (!value) return [];
  if (Array.isArray(value)) return value as T[];
  if (typeof value === 'string') {
    try {
      const parsed = JSON.parse(value);
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  }
  return [];
}