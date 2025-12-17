import { useQuery } from "@tanstack/react-query";
import { API_BASE_URL } from "@/lib/api-url";

// Helper function to get auth token
const getToken = (): string | null => {
  return localStorage.getItem("deepfix_token");
};

// Types
export interface RequestLog {
  id: string;
  user_id: string;
  user_email: string;
  endpoint: string;
  request_json: string | null;
  response_json: string | null;
  status_code: number | null;
  duration_ms: number | null;
  created_at: string;
}

export interface RequestLogListResponse {
  items: RequestLog[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface RequestLogStats {
  total_requests: number;
  total_requests_24h: number;
  total_requests_7d: number;
  total_requests_30d: number;
  avg_duration_ms: number | null;
  endpoints: Record<string, number>;
}

interface UseRequestLogsParams {
  page?: number;
  pageSize?: number;
  fromDate?: string;
  toDate?: string;
  endpoint?: string;
}

// Fetch request logs with pagination and filters
const fetchRequestLogs = async (
  params: UseRequestLogsParams
): Promise<RequestLogListResponse> => {
  const token = getToken();
  if (!token) {
    throw new Error("Not authenticated");
  }

  const searchParams = new URLSearchParams();
  if (params.page) searchParams.set("page", params.page.toString());
  if (params.pageSize) searchParams.set("page_size", params.pageSize.toString());
  if (params.fromDate) searchParams.set("from_date", params.fromDate);
  if (params.toDate) searchParams.set("to_date", params.toDate);
  if (params.endpoint) searchParams.set("endpoint", params.endpoint);

  const url = `${API_BASE_URL}/api/request-logs/?${searchParams.toString()}`;
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch request logs: ${response.statusText}`);
  }

  return response.json();
};

// Fetch request log statistics
const fetchRequestStats = async (): Promise<RequestLogStats> => {
  const token = getToken();
  if (!token) {
    throw new Error("Not authenticated");
  }

  const url = `${API_BASE_URL}/api/request-logs/stats`;
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch request stats: ${response.statusText}`);
  }

  return response.json();
};

// Fetch single request log by ID
const fetchRequestLog = async (id: string): Promise<RequestLog> => {
  const token = getToken();
  if (!token) {
    throw new Error("Not authenticated");
  }

  const url = `${API_BASE_URL}/api/request-logs/${id}`;
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch request log: ${response.statusText}`);
  }

  return response.json();
};

// Hook for fetching paginated request logs
export function useRequestLogs(params: UseRequestLogsParams = {}) {
  return useQuery({
    queryKey: ["request-logs", params],
    queryFn: () => fetchRequestLogs(params),
    staleTime: 30 * 1000, // 30 seconds
  });
}

// Hook for fetching request statistics
export function useRequestStats() {
  return useQuery({
    queryKey: ["request-stats"],
    queryFn: fetchRequestStats,
    staleTime: 60 * 1000, // 1 minute
  });
}

// Hook for fetching a single request log
export function useRequestLog(id: string | null) {
  return useQuery({
    queryKey: ["request-log", id],
    queryFn: () => fetchRequestLog(id!),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
