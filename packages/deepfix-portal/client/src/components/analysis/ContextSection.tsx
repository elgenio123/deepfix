interface ContextSectionProps {
  context: {
    optimization_areas?: unknown;
    constraints?: unknown;
  };
}

export default function ContextSection({ context }: ContextSectionProps) {
  if (!context.optimization_areas && !context.constraints) {
    return null;
  }

  return (
    <div className="rounded-lg border p-4">
      <div className="text-sm font-semibold">Context</div>
      <div className="mt-3 grid gap-3 md:grid-cols-2">
        {context.optimization_areas && (
          <div>
            <div className="text-xs font-medium text-muted-foreground">
              Optimization Areas
            </div>
            <div className="mt-1 text-sm whitespace-pre-wrap">
              {String(context.optimization_areas)}
            </div>
          </div>
        )}
        {context.constraints && (
          <div>
            <div className="text-xs font-medium text-muted-foreground">
              Constraints
            </div>
            <div className="mt-1 text-sm whitespace-pre-wrap">
              {String(context.constraints)}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
