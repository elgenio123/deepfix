import { Severity } from "@/lib/analysis-utils";

export interface Issue {
  agent_name: string;
  analyzed_artifacts?: string;
  severity: Severity;
  finding_description: string;
  finding_evidence: string;
  recommendation_action: string;
  recommendation_rationale: string;
}

interface IssueCardProps {
  issue: Issue;
  index: number;
  showAllAgents: boolean;
}

export default function IssueCard({ issue, index, showAllAgents }: IssueCardProps) {
  return (
    <div className="rounded-lg border p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="text-sm font-semibold">
            {index + 1}. {issue.finding_description}
          </div>
          {showAllAgents && (
            <div className="mt-1 text-xs text-muted-foreground">
              Agent: {issue.agent_name}
              {issue.analyzed_artifacts
                ? ` • Artifacts: ${issue.analyzed_artifacts}`
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
            {issue.finding_evidence}
          </div>
        </div>
        <div>
          <div className="text-xs font-medium text-muted-foreground">
            Action
          </div>
          <div className="mt-1 text-sm whitespace-pre-wrap">
            {issue.recommendation_action}
          </div>
        </div>
      </div>

      {issue.recommendation_rationale && (
        <div className="mt-3">
          <div className="text-xs font-medium text-muted-foreground">
            Rationale
          </div>
          <div className="mt-1 text-sm whitespace-pre-wrap">
            {issue.recommendation_rationale}
          </div>
        </div>
      )}
    </div>
  );
}
