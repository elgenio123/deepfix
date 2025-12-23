import { Badge } from "@/components/ui/badge";
import {
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Severity, SeverityColorResult } from "@/lib/analysis-utils";
import IssueCard, { Issue } from "./IssueCard";

interface SeveritySectionProps {
  severity: string;
  issues: Issue[];
  color: SeverityColorResult;
  showAllAgents: boolean;
}

export default function SeveritySection({
  severity,
  issues,
  color,
  showAllAgents,
}: SeveritySectionProps) {
  const normalized = String(severity).toLowerCase();

  return (
    <AccordionItem value={normalized}>
      <AccordionTrigger className="px-4">
        <div className="flex items-center gap-2">
          <span className={`text-sm font-semibold ${color.text}`}>
            {String(severity).toUpperCase()}
          </span>
          <Badge className={color.badge}>{issues.length}</Badge>
        </div>
      </AccordionTrigger>
      <AccordionContent>
        <div className="px-4 pb-4 space-y-3">
          {issues.map((issue, idx) => (
            <IssueCard
              key={`${issue.agent_name}-${idx}`}
              issue={issue}
              index={idx}
              showAllAgents={showAllAgents}
            />
          ))}
        </div>
      </AccordionContent>
    </AccordionItem>
  );
}
