const isProd = process.env.NODE_ENV === 'production';
const defaultServerUrl = isProd ? 'https://razorrecover-api.onrender.com' : 'http://localhost:8000';
const API_BASE = typeof window !== "undefined" ? "" : (process.env.NEXT_PUBLIC_API_URL || defaultServerUrl);

export async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
    cache: "no-store",
  });

  if (!res.ok) {
    let errorDetail = "API Request Failed";
    try {
      const err = await res.json();
      errorDetail = err.detail || err.message || errorDetail;
    } catch (_) {}
    throw new Error(errorDetail);
  }

  return res.json();
}

export const api = {
  // Dashboard
  getDashboard: () => fetchJson<any>("/api/dashboard"),

  // Recovery Cases
  getCases: (params?: { status?: string; risk_level?: string; search?: string }) => {
    const query = new URLSearchParams();
    if (params?.status) query.set("status", params.status);
    if (params?.risk_level) query.set("risk_level", params.risk_level);
    if (params?.search) query.set("search", params.search);
    return fetchJson<any[]>(`/api/recovery-cases?${query.toString()}`);
  },
  getCaseDetail: (id: string) => fetchJson<any>(`/api/recovery-cases/${id}`),
  analyzeCase: (id: string) => fetchJson<any>(`/api/recovery-cases/${id}/analyze`, { method: "POST" }),
  approveCase: (id: string) => fetchJson<any>(`/api/recovery-cases/${id}/approve`, { method: "POST" }),
  rejectCase: (id: string, reason?: string) =>
    fetchJson<any>(`/api/recovery-cases/${id}/reject?reason=${encodeURIComponent(reason || "Rejected by merchant")}`, {
      method: "POST",
    }),
  executeCase: (id: string) => fetchJson<any>(`/api/recovery-cases/${id}/execute`, { method: "POST" }),
  verifyCase: (id: string) => fetchJson<any>(`/api/recovery-cases/${id}/verify`, { method: "POST" }),

  // Payments & Customers
  getPayments: () => fetchJson<any[]>("/api/payments"),
  getCustomers: (search?: string) => fetchJson<any[]>(`/api/customers${search ? `?search=${search}` : ""}`),
  getCustomerDetail: (id: string) => fetchJson<any>(`/api/customers/${id}`),

  // Audit
  getAuditLogs: (caseId?: string) => fetchJson<any[]>(`/api/audit${caseId ? `?case_id=${caseId}` : ""}`),

  // Evaluations
  getEvaluations: () => fetchJson<any[]>("/api/evaluations"),
  getEvaluationDetail: (id: string) => fetchJson<any>(`/api/evaluations/${id}`),
  runEvaluation: (datasetSize: number = 500) =>
    fetchJson<any>(`/api/evaluations/run?dataset_size=${datasetSize}`, { method: "POST" }),

  // Simulator & Demo
  generateCases: (count: number = 50, scenario?: string) =>
    fetchJson<any>("/api/simulator/generate", {
      method: "POST",
      body: JSON.stringify({ count, scenario }),
    }),
  runDemo: () => fetchJson<any>("/api/simulator/demo/run", { method: "POST" }),

  // Settings
  getSettings: () => fetchJson<any>("/api/settings"),
  updateSettings: (payload: any) =>
    fetchJson<any>("/api/settings", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  // Agent Activity Feed
  getAgentActivity: () => fetchJson<any[]>("/api/agent/activity"),

  // Razorpay Connection
  getRazorpayConnection: () => fetchJson<any>("/api/razorpay/connection"),
  testRazorpayConnection: () => fetchJson<any>("/api/razorpay/test-connection", { method: "POST" }),
  syncRazorpayPayments: () => fetchJson<any>("/api/razorpay/sync/payments", { method: "POST" }),
  syncRazorpayPaymentLinks: () => fetchJson<any>("/api/razorpay/sync/payment-links", { method: "POST" }),

  // Health
  getHealth: () => fetchJson<any>("/api/health"),
};
