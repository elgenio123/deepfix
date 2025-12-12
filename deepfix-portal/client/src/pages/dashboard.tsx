import { useEffect, useState } from "react";
import { useLocation } from "wouter";
import { useAuth } from "@/lib/auth";
import { useRequestStats, RequestLog } from "@/hooks/use-request-logs";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Copy,
  RefreshCw,
  Key,
  BarChart3,
  CreditCard,
  CheckCircle2,
  AlertCircle,
  Trash2,
  History,
  Clock,
  Activity,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import RequestHistoryTab from "@/components/RequestHistoryTab";
import RequestDetailDialog from "@/components/RequestDetailDialog";

export default function Dashboard() {
  const { user, isLoading, generateApiKey, deleteApiKey } = useAuth();
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const [isGenerating, setIsGenerating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [selectedLog, setSelectedLog] = useState<RequestLog | null>(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);

  const { data: stats, isLoading: statsLoading } = useRequestStats();

  const maskedApiKey = user?.apiKey
    ? `${user.apiKey.slice(0, 6)}...${user.apiKey.slice(-4)}`
    : "";

  useEffect(() => {
    if (!isLoading && !user) {
      setLocation("/login");
    }
  }, [user, isLoading, setLocation]);

  if (isLoading || !user) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <RefreshCw className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  const handleCopyKey = () => {
    if (user.apiKey) {
      navigator.clipboard.writeText(user.apiKey);
      toast({
        title: "Copied!",
        description: "API key copied to clipboard.",
      });
    }
  };

  const handleGenerateKey = async () => {
    setIsGenerating(true);
    await generateApiKey();
    setIsGenerating(false);
  };

  const handleDeleteKey = async () => {
    setIsDeleting(true);
    try {
      await deleteApiKey();
      toast({
        title: "API key deleted",
        description: "Generate a new key when you're ready.",
      });
    } finally {
      setIsDeleting(false);
    }
  };

  const handleViewDetails = (log: RequestLog) => {
    setSelectedLog(log);
    setDetailDialogOpen(true);
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-1">Manage your API keys and monitor usage.</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground bg-muted/50 px-3 py-1 rounded-full border">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          System Status: Operational
        </div>
      </div>

      <Tabs defaultValue="api-keys" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3 lg:w-[400px]">
          <TabsTrigger value="api-keys" className="gap-2">
            <Key className="w-4 h-4" />
            <span className="hidden sm:inline">API Keys</span>
          </TabsTrigger>
          <TabsTrigger value="history" className="gap-2">
            <History className="w-4 h-4" />
            <span className="hidden sm:inline">History</span>
          </TabsTrigger>
          <TabsTrigger value="usage" className="gap-2">
            <BarChart3 className="w-4 h-4" />
            <span className="hidden sm:inline">Usage</span>
          </TabsTrigger>
        </TabsList>

        {/* API Keys Tab */}
        <TabsContent value="api-keys">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {/* API Key Card */}
            <Card className="col-span-2 border-primary/20 shadow-md">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Key className="w-5 h-5 text-primary" />
                  API Key Management
                </CardTitle>
                <CardDescription>
                  Your secret key for accessing the DeepFix API. Keep this secure.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {user.apiKey ? (
                  <div className="space-y-4">
                    <div className="relative">
                      <div className="bg-muted p-4 rounded-lg font-mono text-sm break-all pr-12 border">
                        {maskedApiKey}
                      </div>
                      <Button
                        size="icon"
                        variant="ghost"
                        className="absolute right-2 top-2 h-8 w-8 text-muted-foreground hover:text-primary"
                        onClick={handleCopyKey}
                      >
                        <Copy className="w-4 h-4" />
                      </Button>
                    </div>
                    <Alert className="bg-blue-50/50 border-blue-100 text-blue-800 dark:bg-blue-950/20 dark:border-blue-900 dark:text-blue-300">
                      <AlertCircle className="h-4 w-4" />
                      <AlertTitle>Security Tip</AlertTitle>
                      <AlertDescription>
                        Never share your API key in client-side code (browsers, apps). Use it only on your backend.
                      </AlertDescription>
                    </Alert>
                    <div className="flex justify-end">
                      <Button
                        variant="destructive"
                        onClick={handleDeleteKey}
                        disabled={isDeleting}
                        className="flex items-center gap-2"
                      >
                        <Trash2 className={`w-4 h-4 ${isDeleting ? "animate-spin" : ""}`} />
                        {isDeleting ? "Deleting..." : "Delete API Key"}
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 bg-muted/30 rounded-lg border border-dashed">
                    <p className="text-muted-foreground mb-4">You haven't generated an API key yet.</p>
                    <Button onClick={handleGenerateKey} disabled={isGenerating}>
                      {isGenerating ? "Generating..." : "Generate API Key"}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Plan Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CreditCard className="w-5 h-5 text-accent" />
                  Current Plan
                </CardTitle>
                <CardDescription>Your subscription details</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="mb-4">
                  <span className="text-2xl font-bold">Free Tier</span>
                </div>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />{" "}
                    {statsLoading ? "..." : stats?.total_requests_30d || 0} / 100 requests / month
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-500" /> Standard Support
                  </li>
                </ul>
              </CardContent>
              <CardFooter className="border-t bg-muted/10">
                <Button variant="ghost" className="w-full text-primary">Upgrade Plan</Button>
              </CardFooter>
            </Card>
          </div>
        </TabsContent>

        {/* Request History Tab */}
        <TabsContent value="history">
          <Card>
            <CardContent className="pt-6">
              <RequestHistoryTab onViewDetails={handleViewDetails} />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Usage Statistics Tab */}
        <TabsContent value="usage">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {statsLoading ? "-" : stats?.total_requests || 0}
                </div>
                <p className="text-xs text-muted-foreground">All time</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Last 24 Hours</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {statsLoading ? "-" : stats?.total_requests_24h || 0}
                </div>
                <p className="text-xs text-muted-foreground">Requests</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Last 7 Days</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {statsLoading ? "-" : stats?.total_requests_7d || 0}
                </div>
                <p className="text-xs text-muted-foreground">Requests</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg. Latency</CardTitle>
                <RefreshCw className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {statsLoading
                    ? "-"
                    : stats?.avg_duration_ms
                    ? `${(stats.avg_duration_ms / 1000).toFixed(2)}s`
                    : "-"}
                </div>
                <p className="text-xs text-muted-foreground">Response time</p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-primary" />
                Endpoint Breakdown
              </CardTitle>
              <CardDescription>Request distribution by endpoint</CardDescription>
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <RefreshCw className="w-6 h-6 animate-spin text-muted-foreground" />
                </div>
              ) : stats?.endpoints && Object.keys(stats.endpoints).length > 0 ? (
                <div className="space-y-4">
                  {Object.entries(stats.endpoints).map(([endpoint, count]) => (
                    <div key={endpoint} className="flex items-center justify-between">
                      <code className="text-sm bg-muted px-2 py-1 rounded">{endpoint}</code>
                      <span className="font-semibold">{count} requests</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-8 text-center border-2 border-dashed rounded-lg bg-muted/20">
                  <BarChart3 className="w-12 h-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No usage data available yet.</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    Start making API requests to see your usage statistics.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

        </TabsContent>
      </Tabs>

      {/* Request Detail Dialog */}
      <RequestDetailDialog
        log={selectedLog}
        open={detailDialogOpen}
        onOpenChange={setDetailDialogOpen}
      />
    </div>
  );
}
