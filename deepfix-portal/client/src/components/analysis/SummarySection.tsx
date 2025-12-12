interface SummarySectionProps {
  summary: string;
}

export default function SummarySection({ summary }: SummarySectionProps) {
  return (
    <div className="rounded-lg border bg-muted/20 p-4">
      <div className="text-sm font-semibold">Summary</div>
      <div className="mt-2 text-sm text-muted-foreground whitespace-pre-wrap">
        {summary}
      </div>
    </div>
  );
}
