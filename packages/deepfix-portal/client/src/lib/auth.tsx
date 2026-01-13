import React, { createContext, useContext } from "react";
import { useLocation } from "wouter";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { API_BASE_URL } from "@/lib/api-url";
import { getToken, setToken, removeToken, TOKEN_KEY } from "@/lib/token";

type User = {
  id: string;
  name: string | null;
  email: string;
  username: string;
  apiKey: string | null;
  apiKeyId: string | null;
  is_active: boolean;
  is_admin: boolean;
  email_verified: boolean;
  created_at: string;
};

type APIKeyResponse = {
  id: string;
  key: string;
  name: string | null;
  created_at: string;
  last_used: string | null;
  is_active: boolean;
};

type AuthContextType = {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string) => Promise<{ email: string }>;
  verifyEmail: (token: string) => Promise<void>;
  resendVerificationEmail: (email: string) => Promise<void>;
  logout: () => void;
  generateApiKey: () => Promise<void>;
  deleteApiKey: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const parseErrorResponse = async (response: Response) => {
  const responseText = await response.text();
  let errorDetail = "An error occurred";
  try {
    const errorJson = JSON.parse(responseText);
    errorDetail =
      errorJson.detail ||
      errorJson.message ||
      errorJson.error ||
      `HTTP error! status: ${response.status}`;
  } catch {
    errorDetail = responseText || `HTTP error! status: ${response.status}`;
  }
  return errorDetail;
};

// Helper function to make authenticated API calls
const apiCall = async (endpoint: string, options: RequestInit = {}) => {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> ?? {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const url = `${API_BASE_URL}${endpoint}`;
  console.log(`[API] ${options.method || "GET"} ${url}`);

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    console.log(`[API] Response status: ${response.status} ${response.statusText}`);

    if (!response.ok) {
      const errorDetail = await parseErrorResponse(response);
      throw new Error(errorDetail);
    }

    const data = await response.json();
    console.log(`[API] Success:`, data);
    return data;
  } catch (error) {
    console.error(`[API] Request failed:`, error);

    // Handle network errors (server not running, CORS, etc.)
    if (error instanceof TypeError && error.message === "Failed to fetch") {
      const networkError = `Unable to connect to the API server at ${API_BASE_URL}. Please make sure the backend server is running.`;
      console.error(`[API] Network error:`, networkError);
      throw new Error(networkError);
    }
    // Re-throw other errors as-is
    throw error;
  }
};

const fetchCurrentUserWithKeys = async (): Promise<{
  user: User;
  apiKeys: APIKeyResponse[];
} | null> => {
  const token = getToken();
  if (!token) return null;

  const url = `${API_BASE_URL}/api/auth/me/with-keys`;
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (response.status === 401) {
    // Token is invalid or expired; clear and return null
    removeToken();
    return null;
  }

  if (!response.ok) {
    const errorDetail = await parseErrorResponse(response);
    throw new Error(errorDetail);
  }

  const data = await response.json();
  return {
    user: data.user,
    apiKeys: data.api_keys || [],
  };
};

// Legacy function for individual API keys fetch (used by mutations)
const fetchUserApiKeys = async (): Promise<APIKeyResponse[]> => {
  const token = getToken();
  if (!token) return [];

  const url = `${API_BASE_URL}/api/api-keys/`;
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (response.status === 401) {
    removeToken();
    return [];
  }

  if (!response.ok) {
    const errorDetail = await parseErrorResponse(response);
    throw new Error(errorDetail);
  }

  return await response.json();
};

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Single query fetches both user and API keys in one request
  const combinedQuery = useQuery({
    queryKey: ["auth", "me-with-keys"],
    queryFn: fetchCurrentUserWithKeys,
    staleTime: 60 * 1000, // 1 minute
    retry: false,
  });

  const activeKeys = (combinedQuery.data?.apiKeys || [])
    .filter((key) => key.is_active)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
  const primaryKey = activeKeys[0];

  const user: User | null = combinedQuery.data?.user
    ? {
      ...combinedQuery.data.user,
      apiKey: primaryKey?.key || null,
      apiKeyId: primaryKey?.id || null,
    }
    : null;

  const isLoading = combinedQuery.isPending;

  const login = async (email: string, password: string) => {
    try {
      const response = await apiCall("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });

      const { access_token } = response;

      // Store token
      setToken(access_token);

      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["auth", "me-with-keys"] }),
      ]);
      await queryClient.prefetchQuery({ queryKey: ["auth", "me-with-keys"], queryFn: fetchCurrentUserWithKeys });

      toast({
        title: "Welcome back!",
        description: "You have successfully logged in.",
      });
      setLocation("/dashboard");
    } catch (error) {
      toast({
        title: "Login failed",
        description: error instanceof Error ? error.message : "Invalid credentials",
        variant: "destructive",
      });
      throw error;
    }
  };

  const signup = async (name: string, email: string, password: string) => {
    try {
      console.log("Signup attempt:", { name, email, api: `${API_BASE_URL}/api/auth/signup` });
      const response = await apiCall("/api/auth/signup", {
        method: "POST",
        body: JSON.stringify({ name, email, password }),
      });
      console.log("Signup response:", response);

      // Signup no longer returns access_token - user needs to verify email first
      return { email: response.email };
    } catch (error) {
      console.error("Signup error:", error);
      toast({
        title: "Signup failed",
        description: error instanceof Error ? error.message : "Failed to create account",
        variant: "destructive",
      });
      throw error;
    }
  };

  const verifyEmail = async (token: string) => {
    try {
      const response = await apiCall("/api/auth/verify-email", {
        method: "POST",
        body: JSON.stringify({ token }),
      });

      toast({
        title: "Email verified!",
        description: response.message || "You can now log in to your account.",
      });
    } catch (error) {
      toast({
        title: "Verification failed",
        description: error instanceof Error ? error.message : "Invalid or expired verification token",
        variant: "destructive",
      });
      throw error;
    }
  };

  const resendVerificationEmail = async (email: string) => {
    try {
      const response = await apiCall("/api/auth/resend-verification", {
        method: "POST",
        body: JSON.stringify({ email }),
      });

      toast({
        title: "Verification email sent",
        description: response.message || "Please check your inbox for the verification link.",
      });
    } catch (error) {
      toast({
        title: "Failed to resend email",
        description: error instanceof Error ? error.message : "An error occurred",
        variant: "destructive",
      });
      throw error;
    }
  };

  const logout = () => {
    removeToken();
    queryClient.removeQueries({ queryKey: ["auth", "me-with-keys"] });
    toast({
      title: "Logged out",
      description: "See you next time.",
    });
    setLocation("/");
  };

  const generateApiKey = async () => {
    try {
      const response: APIKeyResponse = await apiCall("/api/api-keys/", {
        method: "POST",
        body: JSON.stringify({ name: "Default Key" }),
      });

      // Invalidate to refetch with new key
      await queryClient.invalidateQueries({ queryKey: ["auth", "me-with-keys"] });

      toast({
        title: "API Key Generated",
        description: "Your new API key is ready to use.",
      });
    } catch (error) {
      toast({
        title: "Failed to generate API key",
        description: error instanceof Error ? error.message : "An error occurred",
        variant: "destructive",
      });
      throw error;
    }
  };

  const deleteApiKey = async () => {
    if (!primaryKey?.id) {
      toast({
        title: "No API key to delete",
        description: "Generate an API key first.",
        variant: "destructive",
      });
      return;
    }

    const deletingId = primaryKey.id;

    try {
      await apiCall(`/api/api-keys/${deletingId}`, {
        method: "DELETE",
      });

      await queryClient.invalidateQueries({ queryKey: ["auth", "me-with-keys"] });

      toast({
        title: "API Key deleted",
        description: "You can generate a new key now.",
      });
    } catch (error) {
      // Refetch to ensure UI is in sync
      await queryClient.invalidateQueries({ queryKey: ["auth", "me-with-keys"] });

      toast({
        title: "Failed to delete API key",
        description: error instanceof Error ? error.message : "An error occurred",
        variant: "destructive",
      });
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, signup, verifyEmail, resendVerificationEmail, logout, generateApiKey, deleteApiKey }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
