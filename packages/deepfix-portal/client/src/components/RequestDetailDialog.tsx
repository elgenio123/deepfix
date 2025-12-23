import { RequestLog } from "@/hooks/use-request-logs";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Copy, CheckCircle2 } from "lucide-react";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";
import AnalysisResponseView from "@/components/AnalysisResponseView";

interface RequestDetailDialogProps {
  log: RequestLog | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function RequestDetailDialog({
  log,
  open,
  onOpenChange,
}: RequestDetailDialogProps) {
  const { toast } = useToast();
  const [copiedTab, setCopiedTab] = useState<string | null>(null);

  if (!log) return null;

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("en-US", {
      weekday: "long",
      month: "long",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }).format(date);
  };

  const formatDuration = (ms: number | null) => {
    if (ms === null) return "-";
    if (ms < 1000) return `${Math.round(ms)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const formatJson = (jsonString: string | null): string => {
    if (!jsonString) return "No data available";
    try {
      const parsed = JSON.parse(jsonString);
      return JSON.stringify(parsed, null, 2);
    } catch {
      return jsonString;
    }
  };

  const copyToClipboard = async (text: string, tab: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedTab(tab);
      toast({
        title: "Copied!",
        description: `${tab} copied to clipboard.`,
      });
      setTimeout(() => setCopiedTab(null), 2000);
    } catch {
      toast({
        title: "Failed to copy",
        description: "Please try again.",
        variant: "destructive",
      });
    }
  };

  const getStatusBadge = (statusCode: number | null) => {
    if (statusCode === null) return <Badge variant="outline">Unknown</Badge>;
    if (statusCode >= 200 && statusCode < 300) {
      return <Badge className="bg-green-500 hover:bg-green-600">{statusCode} OK</Badge>;
    }
    if (statusCode >= 400 && statusCode < 500) {
      return <Badge variant="destructive">{statusCode} Error</Badge>;
    }
    if (statusCode >= 500) {
      return <Badge variant="destructive">{statusCode} Server Error</Badge>;
    }
    return <Badge variant="outline">{statusCode}</Badge>;
  };

  const requestJson = formatJson(log.request_json);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <code className="text-sm bg-muted px-2 py-1 rounded">{log.endpoint}</code>
            {getStatusBadge(log.status_code)}
          </DialogTitle>
          <DialogDescription>{formatDate(log.created_at)}</DialogDescription>
        </DialogHeader>

        <div className="grid grid-cols-3 gap-4 py-4 text-sm">
          <div>
            <span className="text-muted-foreground">Duration</span>
            <p className="font-medium">{formatDuration(log.duration_ms)}</p>
          </div>
          <div>
            <span className="text-muted-foreground">User Email</span>
            <p className="font-medium truncate">{log.user_email}</p>
          </div>
          <div>
            <span className="text-muted-foreground">Request ID</span>
            <p className="font-mono text-xs truncate">{log.id}</p>
          </div>
        </div>

        <Tabs defaultValue="request" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="request">Request</TabsTrigger>
            <TabsTrigger value="response">Response</TabsTrigger>
          </TabsList>
          <TabsContent value="request" className="mt-4">
            <div className="relative">
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-2 top-2 z-10"
                onClick={() => copyToClipboard(requestJson, "Request")}
              >
                {copiedTab === "Request" ? (
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
              </Button>
              <ScrollArea className="h-[300px] w-full rounded-md border bg-muted/30">
                <pre className="p-4 text-sm font-mono whitespace-pre-wrap break-all">
                  {requestJson}
                </pre>
              </ScrollArea>
            </div>
          </TabsContent>
          <TabsContent value="response" className="mt-4">
            <AnalysisResponseView
              responseJson={log.response_json}
              meta={{
                endpoint: log.endpoint,
                status_code: log.status_code,
                duration_ms: log.duration_ms,
                created_at: log.created_at,
              }}
            />
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
