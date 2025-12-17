import { useEffect, useState } from "react";
import { useLocation, Link } from "wouter";
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
import { Loader2, CheckCircle2, XCircle, Mail } from "lucide-react";

// Track verification attempts globally (survives HMR and re-renders)
const verificationAttempts = new Set<string>();

export default function VerifyEmail() {
  const [, setLocation] = useLocation();
  const { verifyEmail, resendVerificationEmail } = useAuth();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [isResending, setIsResending] = useState(false);

  useEffect(() => {
    // Get token from URL query parameter
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");

    if (!token) {
      setStatus("error");
      setErrorMessage("No verification token provided. Please check your email for the verification link.");
      return;
    }

    // Check if we've already attempted to verify this token (globally)
    if (verificationAttempts.has(token)) {
      return;
    }

    // Also check sessionStorage to survive page refreshes within the same session
    const sessionKey = `email_verify_${token}`;
    if (sessionStorage.getItem(sessionKey)) {
      // Already attempted in this session - check result
      const result = sessionStorage.getItem(sessionKey);
      if (result === "success") {
        setStatus("success");
      } else if (result === "error") {
        setStatus("error");
        setErrorMessage("Verification already attempted. Please try resending a new verification email.");
      }
      return;
    }

    // Mark token as being verified (prevents duplicate calls)
    verificationAttempts.add(token);
    sessionStorage.setItem(sessionKey, "pending");

    // Verify email with token (only once)
    verifyEmail(token)
      .then(() => {
        sessionStorage.setItem(sessionKey, "success");
        setStatus("success");
      })
      .catch((error) => {
        sessionStorage.setItem(sessionKey, "error");
        setStatus("error");
        setErrorMessage(error instanceof Error ? error.message : "Invalid or expired verification token");
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty deps - only run once on mount

  const handleResend = async () => {
    if (!email) {
      setErrorMessage("Please enter your email address to resend the verification email.");
      return;
    }

    setIsResending(true);
    try {
      await resendVerificationEmail(email);
      setStatus("success");
      setErrorMessage("");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to resend verification email");
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center p-4 bg-muted/20">
      <Card className="w-full max-w-md shadow-lg border-muted">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">
            Email Verification
          </CardTitle>
          <CardDescription className="text-center">
            {status === "loading" && "Verifying your email address..."}
            {status === "success" && "Your email has been verified!"}
            {status === "error" && "Verification failed"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {status === "loading" && (
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto">
                <Loader2 className="w-8 h-8 animate-spin" />
              </div>
              <p className="text-muted-foreground">Please wait while we verify your email...</p>
            </div>
          )}

          {status === "success" && (
            <div className="text-center space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-semibold text-foreground">Email Verified!</h3>
              <p className="text-muted-foreground">
                Your email address has been successfully verified. You can now log in to your account.
              </p>
              <Button
                className="w-full mt-4"
                onClick={() => setLocation("/login")}
              >
                Go to Login
              </Button>
            </div>
          )}

          {status === "error" && (
            <div className="text-center space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="w-16 h-16 bg-red-100 text-red-600 rounded-full flex items-center justify-center mx-auto">
                <XCircle className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-semibold text-foreground">Verification Failed</h3>
              <p className="text-muted-foreground">{errorMessage}</p>

              <div className="pt-4 space-y-4">
                <div className="space-y-2">
                  <label htmlFor="resend-email" className="text-sm font-medium text-foreground">
                    Resend verification email
                  </label>
                  <div className="flex gap-2">
                    <input
                      id="resend-email"
                      type="email"
                      placeholder="your@email.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    />
                    <Button
                      variant="outline"
                      onClick={handleResend}
                      disabled={isResending || !email}
                    >
                      {isResending ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Sending...
                        </>
                      ) : (
                        <>
                          <Mail className="mr-2 h-4 w-4" />
                          Resend
                        </>
                      )}
                    </Button>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  className="w-full"
                  onClick={() => setLocation("/signup")}
                >
                  Back to Sign Up
                </Button>
              </div>
            </div>
          )}
        </CardContent>
        <CardFooter className="flex justify-center border-t bg-muted/10 p-4">
          <Link href="/login">
            <a className="text-sm text-muted-foreground hover:text-primary transition-colors">
              Back to Login
            </a>
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
}
