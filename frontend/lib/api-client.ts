/**
 * API client for communicating with the AgenticOmni backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_VERSION = "v1";

/**
 * API error class for handling backend errors.
 */
export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: unknown
  ) {
    super(message);
    this.name = "APIError";
  }
}

/**
 * Health check response from the backend.
 */
export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
  checks: {
    database: {
      status: string;
      response_time_ms: number;
      error: string | null;
    };
  };
}

/**
 * Generic API request function.
 *
 * @param endpoint - API endpoint path
 * @param options - Fetch options
 * @returns Parsed JSON response
 * @throws {APIError} If the request fails
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}/api/${API_VERSION}${endpoint}`;

  const defaultHeaders: HeadersInit = {
    "Content-Type": "application/json",
  };

  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);

    // Parse response body
    const data = await response.json().catch(() => null);

    if (!response.ok) {
      throw new APIError(
        data?.message || `API request failed: ${response.statusText}`,
        response.status,
        data
      );
    }

    return data as T;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }

    // Network error or other fetch error
    throw new APIError(
      error instanceof Error ? error.message : "Network error",
      0
    );
  }
}

/**
 * Check the health status of the backend API.
 *
 * @returns Health check response
 * @throws {APIError} If the health check fails
 *
 * @example
 * ```ts
 * try {
 *   const health = await healthCheck();
 *   console.log("API Status:", health.status);
 * } catch (error) {
 *   console.error("Health check failed:", error);
 * }
 * ```
 */
export async function healthCheck(): Promise<HealthResponse> {
  return apiRequest<HealthResponse>("/health");
}

/**
 * API client with all available endpoints.
 */
export const api = {
  health: {
    check: healthCheck,
  },
  // Add more API endpoints here as they are implemented
};

export default api;
