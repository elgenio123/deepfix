import { Fragment, useEffect, useState } from "react";
import { useRequestLogs, RequestLog } from "@/hooks/use-request-logs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import AnalysisResponseView from "@/components/AnalysisResponseView";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { ChevronDown, ChevronUp, Eye, RefreshCw, Clock, AlertCircle } from "lucide-react";

interface RequestHistoryTabProps {
  onViewDetails: (log: RequestLog) => void;
}

export default function RequestHistoryTab({ onViewDetails }: RequestHistoryTabProps) {
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  const { data, isLoading, isError, error, refetch, isFetching } = useRequestLogs({
    page,
    pageSize,
  });

  useEffect(() => {
    // Keep UX predictable when paging through history
    setExpandedIds(new Set());
  }, [page]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  };

  const formatDuration = (ms: number | null) => {
    if (ms === null) return "-";
    if (ms < 1000) return `${Math.round(ms)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const getStatusBadge = (statusCode: number | null) => {
    if (statusCode === null) return <Badge variant="outline">Unknown</Badge>;
    if (statusCode >= 200 && statusCode < 300) {
      return <Badge className="bg-green-500 hover:bg-green-600">{statusCode}</Badge>;
    }
    if (statusCode >= 400 && statusCode < 500) {
      return <Badge variant="destructive">{statusCode}</Badge>;
    }
    if (statusCode >= 500) {
      return <Badge variant="destructive">{statusCode}</Badge>;
    }
    return <Badge variant="outline">{statusCode}</Badge>;
  };

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <AlertCircle className="w-12 h-12 text-destructive mb-4" />
        <h3 className="text-lg font-semibold mb-2">Failed to load request history</h3>
        <p className="text-muted-foreground mb-4">
          {error instanceof Error ? error.message : "An error occurred"}
        </p>
        <Button onClick={() => refetch()} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          Try Again
        </Button>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex justify-between items-center mb-4">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-10 w-24" />
        </div>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Duration</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {[...Array(5)].map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-12" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-8 w-20 ml-auto" /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>
    );
  }

  const totalPages = data?.total_pages || 1;
  const hasData = data?.items && data.items.length > 0;

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold">Request History</h3>
          <p className="text-sm text-muted-foreground">
            {data?.total || 0} total requests
          </p>
        </div>
        <Button
          onClick={() => refetch()}
          variant="outline"
          size="sm"
          disabled={isFetching}
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${isFetching ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {!hasData ? (
        <div className="flex flex-col items-center justify-center py-12 text-center border rounded-lg bg-muted/20">
          <Clock className="w-12 h-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">No requests yet</h3>
          <p className="text-muted-foreground">
            Your API request history will appear here once you start using the DeepFix API.
          </p>
        </div>
      ) : (
        <>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Duration</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.items.map((log) => {
                  const isExpanded = expandedIds.has(log.id);
                  return (
                    <Fragment key={log.id}>
                      <TableRow>
                        <TableCell className="font-medium">
                          {formatDate(log.created_at)}
                        </TableCell>
                        <TableCell>{getStatusBadge(log.status_code)}</TableCell>
                        <TableCell>{formatDuration(log.duration_ms)}</TableCell>
                        <TableCell className="text-right">
                          <div className="inline-flex items-center justify-end gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() =>
                                setExpandedIds((prev) => {
                                  const next = new Set(prev);
                                  if (next.has(log.id)) next.delete(log.id);
                                  else next.add(log.id);
                                  return next;
                                })
                              }
                            >
                              {isExpanded ? (
                                <ChevronUp className="w-4 h-4 mr-2" />
                              ) : (
                                <ChevronDown className="w-4 h-4 mr-2" />
                              )}
                              {isExpanded ? "Hide" : "Details"}
                            </Button>

                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => onViewDetails(log)}
                              title="Open request details"
                            >
                              <Eye className="w-4 h-4 mr-2" />
                              View
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>

                      {isExpanded && (
                        <TableRow>
                          <TableCell colSpan={4} className="bg-muted/10 p-0">
                            <div className="p-4">
                              <AnalysisResponseView
                                responseJson={log.response_json}
                                meta={{
                                  endpoint: log.endpoint,
                                  status_code: log.status_code,
                                  duration_ms: log.duration_ms,
                                  created_at: log.created_at,
                                }}
                              />
                            </div>
                          </TableCell>
                        </TableRow>
                      )}
                    </Fragment>
                  );
                })}
              </TableBody>
            </Table>
          </div>

          {totalPages > 1 && (
            <Pagination>
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    className={page <= 1 ? "pointer-events-none opacity-50" : "cursor-pointer"}
                  />
                </PaginationItem>
                {[...Array(Math.min(5, totalPages))].map((_, i) => {
                  const pageNum = i + 1;
                  return (
                    <PaginationItem key={pageNum}>
                      <PaginationLink
                        onClick={() => setPage(pageNum)}
                        isActive={page === pageNum}
                        className="cursor-pointer"
                      >
                        {pageNum}
                      </PaginationLink>
                    </PaginationItem>
                  );
                })}
                {totalPages > 5 && (
                  <PaginationItem>
                    <span className="px-2 text-muted-foreground">...</span>
                  </PaginationItem>
                )}
                <PaginationItem>
                  <PaginationNext
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    className={page >= totalPages ? "pointer-events-none opacity-50" : "cursor-pointer"}
                  />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
          )}
        </>
      )}
    </div>
  );
}
