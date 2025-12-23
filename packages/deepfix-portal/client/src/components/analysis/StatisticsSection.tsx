import { Badge } from "@/components/ui/badge";
import { severityColor } from "@/lib/analysis-utils";
import { Issue } from "./IssueCard";

interface StatisticsSectionProps {
  issues: Issue[];
  severityCounts: Map<string, number>;
  orderedSeverities: string[];
}

export default function StatisticsSection({
  issues,
  severityCounts,
  orderedSeverities,
}: StatisticsSectionProps) {
  return (
    <div className="rounded-lg border p-4">
      <div className="text-sm font-semibold">Summary Statistics</div>
      <div className="mt-3 grid gap-3 md:grid-cols-2">
        <div className="flex items-center justify-between rounded-md bg-muted/30 px-3 py-2">
          <span className="text-xs text-muted-foreground">Total Findings</span>
          <span className="text-sm font-semibold">{issues.length}</span>
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
  );
}
