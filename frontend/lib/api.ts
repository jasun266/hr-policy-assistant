// Typed client for the FastAPI backend. Every call is a plain fetch; the demo "auth" is the
// X-Employee-Id header carrying the user picked in the header switcher.

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Role = "employee" | "manager";
export type LeaveType = "annual" | "sick" | "casual";
export type RequestStatus = "draft" | "pending" | "approved" | "rejected" | "cancelled";

export interface Employee {
  id: string;
  name: string;
  role: Role;
}

export interface Health {
  status: string;
  llm: "FakeLLM" | "ClaudeLLM";
}

export interface Balance {
  leave_type: LeaveType;
  entitled: number;
  used: number;
  pending: number;
  remaining: number;
}

export interface LeaveRequest {
  id: number;
  employee_id: string;
  leave_type: LeaveType;
  start_date: string; // ISO date, e.g. "2026-11-15"
  end_date: string;
  days: number; // working days
  reason: string;
  status: RequestStatus;
}

export interface TeamRequest extends LeaveRequest {
  employee_name: string;
}

export interface Citation {
  document: string;
  section: string;
}

export interface ToolStep {
  tool: string;
  input: Record<string, unknown>;
  is_error: boolean;
  output: string;
}

export interface ChatResponse {
  conversation_id: string;
  reply: string;
  stop_reason: string;
  steps: ToolStep[];
  citations: Citation[];
  drafts: LeaveRequest[];
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
  ) {
    super(message);
  }
}

// FastAPI errors come back as {detail: string}, {detail: {code, message}} or a 422 {detail: [...]}.
function toApiError(status: number, body: unknown): ApiError {
  const detail = (body as { detail?: unknown } | null)?.detail;
  if (typeof detail === "string") return new ApiError(detail, status);
  if (detail && typeof detail === "object" && "message" in detail) {
    const d = detail as { code?: string; message: string };
    return new ApiError(d.message, status, d.code);
  }
  return new ApiError(`Request failed (HTTP ${status}).`, status);
}

async function request<T>(path: string, employeeId?: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (employeeId) headers.set("X-Employee-Id", employeeId);
  if (init.body) headers.set("Content-Type", "application/json");

  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, { ...init, headers });
  } catch {
    throw new ApiError(`Can't reach the API at ${API_URL}. Is the backend running?`, 0);
  }
  const body = await res.json().catch(() => null);
  if (!res.ok) throw toApiError(res.status, body);
  return body as T;
}

const post = { method: "POST" };

export const api = {
  health: () => request<Health>("/api/health"),
  employees: () => request<Employee[]>("/api/employees"),

  balance: (me: string) => request<Balance[]>("/api/me/balance", me),
  myRequests: (me: string) => request<LeaveRequest[]>("/api/me/requests", me),
  confirm: (me: string, id: number) => request<LeaveRequest>(`/api/me/requests/${id}/confirm`, me, post),
  cancel: (me: string, id: number) => request<LeaveRequest>(`/api/me/requests/${id}/cancel`, me, post),

  teamRequests: (me: string) => request<TeamRequest[]>("/api/team/requests", me),
  decide: (me: string, id: number, decision: "approve" | "reject") =>
    request<LeaveRequest>(`/api/team/requests/${id}/${decision}`, me, post),

  chat: (me: string, message: string, conversationId?: string) =>
    request<ChatResponse>("/api/chat", me, {
      method: "POST",
      body: JSON.stringify({ message, conversation_id: conversationId }),
    }),
};
