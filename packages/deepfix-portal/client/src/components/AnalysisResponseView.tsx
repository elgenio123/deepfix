import { useId, useMemo, useState } from "react";
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
import { Accordion } from "@/components/ui/accordion";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Copy, Search, X } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import {
  CROSS_ARTIFACT_AGENT,
  Severity,
  formatDuration,
  formatDate,
  statusBadge,
  prettyJson,
  getOrderedSeverities,
  severityColor,
} from "@/lib/analysis-utils";
import SummarySection from "./analysis/SummarySection";
import ContextSection from "./analysis/ContextSection";
import StatisticsSection from "./analysis/StatisticsSection";
import SeveritySection from "./analysis/SeveritySection";
import { Issue } from "./analysis/IssueCard";

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

export default function AnalysisResponseView({
  responseJson,
  meta,
  defaultConcise = true,
}: AnalysisResponseViewProps) {
  const { toast } = useToast();
  const [copied, setCopied] = useState(false);
  const [showAllAgents, setShowAllAgents] = useState(!defaultConcise);
  const [searchQuery, setSearchQuery] = useState("");
  const [severityFilters, setSeverityFilters] = useState<Set<string>>(new Set());
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
        issues: [] as Issue[],
        errorMessages: null as APIResponse["error_messages"],
        hadCrossAgent: false,
        agentsAvailable: [] as string[],
      };
    }

    const api = parsed.value;
    const agentResults = api.agent_results ?? {};
    const agentsAvailable = Object.keys(agentResults);
    const hadCrossAgent = CROSS_ARTIFACT_AGENT in agentResults;

    const agentEntries: Array<[string, AgentResult]> = Object.entries(agentResults);

    const filteredEntries = showAllAgents
      ? agentEntries
      : hadCrossAgent
        ? agentEntries.filter(([name]) => name === CROSS_ARTIFACT_AGENT)
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

  // Filter issues based on search and severity filters
  const filteredIssues = useMemo(() => {
    return report.issues.filter((issue) => {
      // Search filter
      const matchesSearch =
        !searchQuery ||
        issue.finding_description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        issue.finding_evidence.toLowerCase().includes(searchQuery.toLowerCase()) ||
        issue.recommendation_action.toLowerCase().includes(searchQuery.toLowerCase());

      // Severity filter
      const matchesSeverity =
        severityFilters.size === 0 ||
        severityFilters.has(String(issue.severity).toLowerCase());

      return matchesSearch && matchesSeverity;
    });
  }, [report.issues, searchQuery, severityFilters]);

  const severityCounts = useMemo(() => {
    const counts = new Map<string, number>();
    for (const i of filteredIssues) {
      const key = String(i.severity).toLowerCase();
      counts.set(key, (counts.get(key) ?? 0) + 1);
    }
    return counts;
  }, [filteredIssues]);

  const orderedSeverities = useMemo(
    () => getOrderedSeverities(filteredIssues.map((i) => ({ severity: i.severity }))),
    [filteredIssues]
  );

  const toggleSeverityFilter = (severity: string) => {
    const newFilters = new Set(severityFilters);
    if (newFilters.has(severity)) {
      newFilters.delete(severity);
    } else {
      newFilters.add(severity);
    }
    setSeverityFilters(newFilters);
  };

  const clearFilters = () => {
    setSearchQuery("");
    setSeverityFilters(new Set());
  };

  const hasActiveFilters = searchQuery !== "" || severityFilters.size > 0;

  const copyRaw = async () => {
    try {
      await navigator.clipboard.writeText(raw);
      setCopied(true);
      toast({
        title: "Copied!",
        description: "Response copied to clipboard.",
      });
      setTimeout(() => setCopied(false), 1500);
    } catch {
      toast({
        title: "Copy failed",
        description: "Unable to copy to clipboard. Please try again.",
        variant: "destructive",
      });
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
              {CROSS_ARTIFACT_AGENT} was not found in this response. Showing all available agents: {report.agentsAvailable.join(", ")}.
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
            {report.errorMessages && Object.values(report.errorMessages).some(msg => msg !== null) && (
              <Alert variant="destructive">
                <AlertTitle>Some agents failed</AlertTitle>
                <AlertDescription>
                  <ul className="list-disc pl-4 space-y-1 mt-2">
                    {Object.entries(report.errorMessages)
                      .filter(([_, msg]) => msg !== null)
                      .map(([agent, msg]) => (
                        <li key={agent} className="text-sm">
                          <span className="font-semibold">{agent}:</span>{" "}
                          <span className="whitespace-pre-wrap">{msg ?? "Unknown error"}</span>
                        </li>
                      ))}
                  </ul>
                </AlertDescription>
              </Alert>
            )}

            {report.summary && <SummarySection summary={report.summary} />}

            {report.context && report.context.optimization_areas || report.context?.constraints ? (
              <ContextSection context={report.context} />
            ) : null}

            <StatisticsSection
              issues={filteredIssues}
              severityCounts={severityCounts}
              orderedSeverities={orderedSeverities}
            />

            {/* Search and Filter UI */}
            {report.issues.length > 0 && (
              <div className="rounded-lg border p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="text-sm font-semibold">Search & Filter</div>
                  {hasActiveFilters && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={clearFilters}
                      className="h-7 text-xs"
                    >
                      <X className="w-3 h-3 mr-1" />
                      Clear filters
                    </Button>
                  )}
                </div>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    placeholder="Search findings, evidence, or actions..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9"
                  />
                </div>
                <div className="flex flex-wrap gap-2">
                  <span className="text-xs text-muted-foreground self-center">Filter by severity:</span>
                  {["high", "medium", "low"].map((sev) => {
                    const isActive = severityFilters.has(sev);
                    const color = severityColor(sev);
                    return (
                      <Badge
                        key={sev}
                        variant={isActive ? "default" : "outline"}
                        className={`cursor-pointer ${isActive ? color.badge : ""}`}
                        onClick={() => toggleSeverityFilter(sev)}
                      >
                        {sev.toUpperCase()}
                      </Badge>
                    );
                  })}
                </div>
                {hasActiveFilters && (
                  <div className="text-xs text-muted-foreground">
                    Showing {filteredIssues.length} of {report.issues.length} findings
                  </div>
                )}
              </div>
            )}

            <div className="rounded-lg border">
              <div className="px-4 py-3">
                <div className="text-sm font-semibold">Issues by Severity</div>
                <div className="text-xs text-muted-foreground mt-1">
                  Finding • Evidence • Action • Rationale
                </div>
              </div>
              <Separator />

              {filteredIssues.length === 0 ? (
                <div className="p-8 text-center">
                  {report.issues.length === 0 ? (
                    <>
                      <CheckCircle2 className="w-12 h-12 mx-auto mb-3 text-green-500" />
                      <div className="text-sm font-medium">No issues found</div>
                      <div className="text-xs text-muted-foreground mt-1">
                        The analysis completed successfully with no findings to report.
                      </div>
                    </>
                  ) : (
                    <>
                      <Search className="w-12 h-12 mx-auto mb-3 text-muted-foreground" />
                      <div className="text-sm font-medium">No matching findings</div>
                      <div className="text-xs text-muted-foreground mt-1">
                        Try adjusting your search or filter criteria.
                      </div>
                    </>
                  )}
                </div>
              ) : (
                <Accordion type="multiple" className="w-full" defaultValue={orderedSeverities}>
                  {orderedSeverities.map((sev) => {
                    const normalized = String(sev).toLowerCase();
                    const items = filteredIssues.filter(
                      (i) => String(i.severity).toLowerCase() === normalized
                    );
                    const color = severityColor(sev);
                    return (
                      <SeveritySection
                        key={normalized}
                        severity={sev}
                        issues={items}
                        color={color}
                        showAllAgents={showAllAgents}
                      />
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
                aria-label="Copy raw JSON to clipboard"
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
