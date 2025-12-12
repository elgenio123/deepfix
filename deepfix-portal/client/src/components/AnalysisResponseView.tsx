import { useId, useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { CheckCircle2, Copy } from "lucide-react";

type Severity = "high" | "medium" | "low" | string;

interface Finding {
  description: string;
  evidence: string;
  severity: Severity;
  confidence?: number;
}

interface Recommendation {
  action: string;
  rationale: string;
  confidence?: number;
}

interface Analysis {
  findings: Finding;
  recommendations: Recommendation;
}

interface AgentResult {
  agent_name: string;
  analysis: Analysis[];
  analyzed_artifacts?: string[] | null;
  retrieved_knowledge?: string[] | null;
  additional_outputs?: Record<string, unknown>;
  error_message?: string | null;
}

interface APIResponse {
  agent_results?: Record<string, AgentResult>;
  summary?: string | null;
  additional_outputs?: Record<string, unknown>;
  error_messages?: Record<string, string | null> | null;
}

export interface AnalysisResponseViewMeta {
  endpoint?: string;
  status_code?: number | null;
  duration_ms?: number | null;
  created_at?: string;
}

interface AnalysisResponseViewProps {
  responseJson: string | null;
  meta?: AnalysisResponseViewMeta;
  defaultConcise?: boolean;
}

function formatDuration(ms: number | null | undefined) {
  if (ms === null || ms === undefined) return "-";
  if (ms < 1000) return `${Math.round(ms)}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

function formatDate(dateString: string | undefined) {
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

function severityColor(sev: Severity) {
  const s = String(sev).toLowerCase();
  if (s === "high") return { badge: "bg-red-500 hover:bg-red-600", text: "text-red-600" };
  if (s === "medium") return { badge: "bg-yellow-500 hover:bg-yellow-600", text: "text-yellow-700" };
  if (s === "low") return { badge: "bg-green-500 hover:bg-green-600", text: "text-green-700" };
  return { badge: "bg-muted text-foreground", text: "text-foreground" };
}

function statusBadge(statusCode: number | null | undefined) {
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

function prettyJson(jsonString: string | null): string {
  if (!jsonString) return "No data available";
  try {
    const parsed = JSON.parse(jsonString);
    return JSON.stringify(parsed, null, 2);
  } catch {
    return jsonString;
  }
}

function getOrderedSeverities(found: Array<{ severity: Severity }>) {
  const uniq = new Set(found.map((f) => String(f.severity).toLowerCase()));
  const ordered = ["high", "medium", "low"];
  const rest = [...uniq].filter((s) => !ordered.includes(s)).sort();
  return [...ordered.filter((s) => uniq.has(s)), ...rest];
}

export default function AnalysisResponseView({
  responseJson,
  meta,
  defaultConcise = true,
}: AnalysisResponseViewProps) {
  const [copied, setCopied] = useState(false);
  const [showAllAgents, setShowAllAgents] = useState(!defaultConcise);
  const showAllAgentsId = useId();

  const raw = useMemo(() => prettyJson(responseJson), [responseJson]);

  const parsed = useMemo(() => {
    if (!responseJson) return { ok: false as const, error: "No response body" };
    try {
      const obj = JSON.parse(responseJson) as APIResponse;
      return { ok: true as const, value: obj };
    } catch {
      return { ok: false as const, error: "Response is not valid JSON" };
    }
  }, [responseJson]);

  const report = useMemo(() => {
    if (!parsed.ok) {
      return {
        summary: null as string | null,
        context: null as { optimization_areas?: unknown; constraints?: unknown } | null,
        issues: [] as Array<{
          agent_name: string;
          analyzed_artifacts?: string;
          severity: Severity;
          finding_description: string;
          finding_evidence: string;
          recommendation_action: string;
          recommendation_rationale: string;
        }>,
        errorMessages: null as APIResponse["error_messages"],
        hadCrossAgent: false,
        agentsAvailable: [] as string[],
      };
    }

    const api = parsed.value;
    const agentResults = api.agent_results ?? {};
    const agentsAvailable = Object.keys(agentResults);
    const hadCrossAgent = Object.prototype.hasOwnProperty.call(
      agentResults,
      "CrossArtifactReasoningAgent"
    );

    const agentEntries: Array<[string, AgentResult]> = Object.entries(agentResults);

    const filteredEntries = showAllAgents
      ? agentEntries
      : hadCrossAgent
        ? agentEntries.filter(([name]) => name === "CrossArtifactReasoningAgent")
        : agentEntries;

    const issues = filteredEntries.flatMap(([agentName, agent]) => {
      const analyzedArtifacts = agent.analyzed_artifacts?.join(", ") ?? "";
      return (agent.analysis ?? []).map((a) => ({
        agent_name: agentName,
        analyzed_artifacts: analyzedArtifacts,
        severity: a.findings?.severity ?? "unknown",
        finding_description: a.findings?.description ?? "",
        finding_evidence: a.findings?.evidence ?? "",
        recommendation_action: a.recommendations?.action ?? "",
        recommendation_rationale: a.recommendations?.rationale ?? "",
      }));
    });

    const context = {
      optimization_areas: api.additional_outputs?.["optimization_areas"],
      constraints: api.additional_outputs?.["constraints"],
    };

    return {
      summary: api.summary ?? null,
      context,
      issues,
      errorMessages: api.error_messages ?? null,
      hadCrossAgent,
      agentsAvailable,
    };
  }, [parsed, showAllAgents]);

  const severityCounts = useMemo(() => {
    const counts = new Map<string, number>();
    for (const i of report.issues) {
      const key = String(i.severity).toLowerCase();
      counts.set(key, (counts.get(key) ?? 0) + 1);
    }
    return counts;
  }, [report.issues]);

  const orderedSeverities = useMemo(
    () => getOrderedSeverities(report.issues.map((i) => ({ severity: i.severity }))),
    [report.issues]
  );

  const copyRaw = async () => {
    try {
      await navigator.clipboard.writeText(raw);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // ignore
    }
  };

  return (
    <Card className="border-muted-foreground/20">
      <CardHeader className="space-y-2">
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <CardTitle className="text-base">DeepFix Analysis Result</CardTitle>
            <CardDescription className="mt-1">
              {meta?.endpoint ? (
                <span className="inline-flex items-center gap-2">
                  <code className="text-xs bg-muted px-2 py-1 rounded">
                    {meta.endpoint}
                  </code>
                  {statusBadge(meta.status_code)}
                  <span className="text-xs text-muted-foreground">
                    {formatDuration(meta.duration_ms)}
                    {meta.created_at ? ` • ${formatDate(meta.created_at)}` : ""}
                  </span>
                </span>
              ) : (
                "Formatted analysis response"
              )}
            </CardDescription>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2">
              <Switch
                id={showAllAgentsId}
                checked={showAllAgents}
                onCheckedChange={setShowAllAgents}
              />
              <Label htmlFor={showAllAgentsId} className="text-xs text-muted-foreground">
                Show all agents
              </Label>
            </div>
          </div>
        </div>

        {!parsed.ok && (
          <Alert variant="destructive">
            <AlertTitle>Unable to render report</AlertTitle>
            <AlertDescription>{parsed.error}. Showing raw response.</AlertDescription>
          </Alert>
        )}

        {parsed.ok && !showAllAgents && !report.hadCrossAgent && report.agentsAvailable.length > 0 && (
          <Alert>
            <AlertTitle>Concise agent not available</AlertTitle>
            <AlertDescription>
              CrossArtifactReasoningAgent was not found in this response. Showing all available agents: {report.agentsAvailable.join(", ")}.
            </AlertDescription>
          </Alert>
        )}
      </CardHeader>

      <CardContent>
        <Tabs defaultValue="report" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="report">Report</TabsTrigger>
            <TabsTrigger value="raw">Raw JSON</TabsTrigger>
          </TabsList>

          <TabsContent value="report" className="mt-4 space-y-4">
            {report.errorMessages && Object.keys(report.errorMessages).length > 0 && (
              <Alert variant="destructive">
                <AlertTitle>Some agents failed</AlertTitle>
                <AlertDescription>
                  {Object.entries(report.errorMessages)
                    .map(([agent, msg]) => `${agent}: ${msg ?? "Unknown error"}`)
                    .join(" • ")}
                </AlertDescription>
              </Alert>
            )}

            {report.summary && (
              <div className="rounded-lg border bg-muted/20 p-4">
                <div className="text-sm font-semibold">Summary</div>
                <div className="mt-2 text-sm text-muted-foreground whitespace-pre-wrap">
                  {report.summary}
                </div>
              </div>
            )}

            {(report.context?.optimization_areas || report.context?.constraints) && (
              <div className="rounded-lg border p-4">
                <div className="text-sm font-semibold">Context</div>
                <div className="mt-3 grid gap-3 md:grid-cols-2">
                  {report.context?.optimization_areas && (
                    <div>
                      <div className="text-xs font-medium text-muted-foreground">
                        Optimization Areas
                      </div>
                      <div className="mt-1 text-sm whitespace-pre-wrap">
                        {String(report.context.optimization_areas)}
                      </div>
                    </div>
                  )}
                  {report.context?.constraints && (
                    <div>
                      <div className="text-xs font-medium text-muted-foreground">
                        Constraints
                      </div>
                      <div className="mt-1 text-sm whitespace-pre-wrap">
                        {String(report.context.constraints)}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            <div className="rounded-lg border p-4">
              <div className="text-sm font-semibold">Summary Statistics</div>
              <div className="mt-3 grid gap-3 md:grid-cols-2">
                <div className="flex items-center justify-between rounded-md bg-muted/30 px-3 py-2">
                  <span className="text-xs text-muted-foreground">Total Findings</span>
                  <span className="text-sm font-semibold">{report.issues.length}</span>
                </div>
                <div className="flex items-center justify-between rounded-md bg-muted/30 px-3 py-2">
                  <span className="text-xs text-muted-foreground">Severity Distribution</span>
                  <span className="flex flex-wrap items-center justify-end gap-2">
                    {orderedSeverities.length === 0 ? (
                      <span className="text-xs text-muted-foreground">-</span>
                    ) : (
                      orderedSeverities.map((sev) => {
                        const c = severityCounts.get(sev) ?? 0;
                        const color = severityColor(sev);
                        return (
                          <Badge key={sev} className={color.badge}>
                            {sev.toUpperCase()}: {c}
                          </Badge>
                        );
                      })
                    )}
                  </span>
                </div>
              </div>
            </div>

            <div className="rounded-lg border">
              <div className="px-4 py-3">
                <div className="text-sm font-semibold">Issues by Severity</div>
                <div className="text-xs text-muted-foreground mt-1">
                  Finding • Evidence • Action • Rationale
                </div>
              </div>
              <Separator />

              {report.issues.length === 0 ? (
                <div className="p-4 text-sm text-muted-foreground">
                  No findings available in this response.
                </div>
              ) : (
                <Accordion type="multiple" className="w-full" defaultValue={orderedSeverities}>
                  {orderedSeverities.map((sev) => {
                    const normalized = String(sev).toLowerCase();
                    const items = report.issues.filter(
                      (i) => String(i.severity).toLowerCase() === normalized
                    );
                    const color = severityColor(sev);
                    return (
                      <AccordionItem key={normalized} value={normalized}>
                        <AccordionTrigger className="px-4">
                          <div className="flex items-center gap-2">
                            <span className={`text-sm font-semibold ${color.text}`}>
                              {String(sev).toUpperCase()}
                            </span>
                            <Badge className={color.badge}>{items.length}</Badge>
                          </div>
                        </AccordionTrigger>
                        <AccordionContent>
                          <div className="px-4 pb-4 space-y-3">
                            {items.map((i, idx) => (
                              <div key={`${i.agent_name}-${idx}`} className="rounded-lg border p-4">
                                <div className="flex items-start justify-between gap-3">
                                  <div className="min-w-0">
                                    <div className="text-sm font-semibold">
                                      {idx + 1}. {i.finding_description}
                                    </div>
                                    {showAllAgents && (
                                      <div className="mt-1 text-xs text-muted-foreground">
                                        Agent: {i.agent_name}
                                        {i.analyzed_artifacts
                                          ? ` • Artifacts: ${i.analyzed_artifacts}`
                                          : ""}
                                      </div>
                                    )}
                                  </div>
                                </div>

                                <div className="mt-3 grid gap-3 md:grid-cols-2">
                                  <div>
                                    <div className="text-xs font-medium text-muted-foreground">
                                      Evidence
                                    </div>
                                    <div className="mt-1 text-sm whitespace-pre-wrap">
                                      {i.finding_evidence}
                                    </div>
                                  </div>
                                  <div>
                                    <div className="text-xs font-medium text-muted-foreground">
                                      Action
                                    </div>
                                    <div className="mt-1 text-sm whitespace-pre-wrap">
                                      {i.recommendation_action}
                                    </div>
                                  </div>
                                </div>

                                {i.recommendation_rationale && (
                                  <div className="mt-3">
                                    <div className="text-xs font-medium text-muted-foreground">
                                      Rationale
                                    </div>
                                    <div className="mt-1 text-sm whitespace-pre-wrap">
                                      {i.recommendation_rationale}
                                    </div>
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </AccordionContent>
                      </AccordionItem>
                    );
                  })}
                </Accordion>
              )}
            </div>
          </TabsContent>

          <TabsContent value="raw" className="mt-4">
            <div className="relative">
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-2 top-2 z-10"
                onClick={copyRaw}
              >
                {copied ? (
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
              </Button>
              <ScrollArea className="h-[360px] w-full rounded-md border bg-muted/30">
                <pre className="p-4 text-sm font-mono whitespace-pre-wrap break-all">
                  {raw}
                </pre>
              </ScrollArea>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
