import { Badge } from "@/components/ui/badge";

// Constants
export const CROSS_ARTIFACT_AGENT = "CrossArtifactReasoningAgent";
export const SEVERITY_ORDER = ["high", "medium", "low"] as const;

// Types
export type Severity = "high" | "medium" | "low" | string;

export interface SeverityColorResult {
  badge: string;
  text: string;
}

// Utility Functions
export function formatDuration(ms: number | null | undefined): string {
  if (ms === null || ms === undefined) return "-";
  if (ms < 1000) return `${Math.round(ms)}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

export function formatDate(dateString: string | undefined): string {
  if (!dateString) return "";
  const date = new Date(dateString);
  if (Number.isNaN(date.getTime())) return dateString;
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

export function severityColor(sev: Severity): SeverityColorResult {
  const s = String(sev).toLowerCase();
  if (s === "high") return { badge: "bg-red-500 hover:bg-red-600", text: "text-red-600" };
  if (s === "medium") return { badge: "bg-yellow-500 hover:bg-yellow-600", text: "text-yellow-700" };
  if (s === "low") return { badge: "bg-green-500 hover:bg-green-600", text: "text-green-700" };
  return { badge: "bg-muted text-foreground", text: "text-foreground" };
}

export function statusBadge(statusCode: number | null | undefined): JSX.Element {
  if (statusCode === null || statusCode === undefined) {
    return <Badge variant="outline">Unknown</Badge>;
  }
  if (statusCode >= 200 && statusCode < 300) {
    return <Badge className="bg-green-500 hover:bg-green-600">{statusCode}</Badge>;
  }
  if (statusCode >= 400 && statusCode < 600) {
    return <Badge variant="destructive">{statusCode}</Badge>;
  }
  return <Badge variant="outline">{statusCode}</Badge>;
}

export function prettyJson(jsonString: string | null): string {
  if (!jsonString) return "No data available";
  try {
    const parsed = JSON.parse(jsonString);
    return JSON.stringify(parsed, null, 2);
  } catch {
    return jsonString;
  }
}

export function getOrderedSeverities(found: Array<{ severity: Severity }>): string[] {
  const uniq = new Set(found.map((f) => String(f.severity).toLowerCase()));
  const rest = [...uniq].filter((s) => !SEVERITY_ORDER.includes(s as any)).sort();
  return [...SEVERITY_ORDER.filter((s) => uniq.has(s)), ...rest];
}
