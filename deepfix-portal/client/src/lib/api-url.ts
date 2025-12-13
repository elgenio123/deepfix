/**
 * Get the base URL for API requests.
 *
 * Priority:
 * 1. Explicit override from build-time env (VITE_API_URL)
 * 2. Development mode (Vite dev server on port 5173) -> localhost:5041
 * 3. Production: use same-origin (empty string) since Caddy or Traefik will proxy /api/*
 */
export function getApiBaseUrl(): string {
  // 1. Explicit override from build-time env
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  // 2. Development mode (Vite dev server on port 5173)
  if (typeof window !== "undefined" && window.location.port === "5173") {
    return "http://localhost:5041";
  }
  // 3. Production: use same-origin (Caddy or Traefik will proxy /api/*)
  return "";
}

/**
 * Pre-computed API base URL for use in modules.
 * For most cases, use this constant instead of calling getApiBaseUrl() repeatedly.
 */
export const API_BASE_URL = getApiBaseUrl();
