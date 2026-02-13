import axios, { type AxiosRequestConfig } from "axios";

// Axios 인스턴스 (향후 interceptor 추가 가능)
const http = axios.create();

// --- projectId 글로벌 리졸버 ---
let _projectIdResolver: (() => string) | null = null;

export function setProjectIdResolver(resolver: () => string): void {
  _projectIdResolver = resolver;
}

export function getProjectId(): string {
  if (!_projectIdResolver) {
    console.warn("[api] projectId resolver가 설정되지 않았습니다.");
    return "";
  }
  return _projectIdResolver();
}

// --- API 헬퍼 ---
export const api = {
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const res = await http.get<T>(url, config);
    return res.data;
  },
  async post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const res = await http.post<T>(url, data, config);
    return res.data;
  },
  async put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const res = await http.put<T>(url, data, config);
    return res.data;
  },
  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const res = await http.delete<T>(url, config);
    return res.data;
  },
};

// 고급 사용 시 인스턴스 직접 접근
export { http };
