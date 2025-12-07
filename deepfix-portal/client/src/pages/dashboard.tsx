import { useEffect, useState } from "react";
import { useLocation } from "wouter";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Copy,
  RefreshCw,
  Key,
  BarChart3,
  CreditCard,
  CheckCircle2,
  AlertCircle,
  Trash2,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function Dashboard() {
  const { user, isLoading, generateApiKey, deleteApiKey } = useAuth();
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const [isGenerating, setIsGenerating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

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

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8">
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
                <CheckCircle2 className="w-4 h-4 text-green-500" /> 100 requests / month
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

      {/* Usage Statistics 
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-primary" />
            Usage Statistics
          </CardTitle>
          <CardDescription>Real-time monitoring of your API consumption</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Endpoint</TableHead>
                <TableHead>Method</TableHead>
                <TableHead>Requests (24h)</TableHead>
                <TableHead>Avg. Latency</TableHead>
                <TableHead className="text-right">Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">/v1/completions</TableCell>
                <TableCell><span className="inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10">POST</span></TableCell>
                <TableCell>0</TableCell>
                <TableCell>-</TableCell>
                <TableCell className="text-right"><span className="text-green-500 font-medium">Active</span></TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">/v1/embeddings</TableCell>
                <TableCell><span className="inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10">POST</span></TableCell>
                <TableCell>0</TableCell>
                <TableCell>-</TableCell>
                <TableCell className="text-right"><span className="text-green-500 font-medium">Active</span></TableCell>
              </TableRow>
            </TableBody>
          </Table>
          <div className="mt-8 h-48 flex items-center justify-center border-2 border-dashed rounded-lg bg-muted/20">
            <p className="text-muted-foreground text-sm">No usage data available for this period.</p>
          </div>
        </CardContent>
      </Card>
      */}
    </div>
  );
}
