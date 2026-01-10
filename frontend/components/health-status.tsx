/**
 * Health Status Component
 * 
 * Displays the current health status of the backend API.
 */

"use client";

import { useEffect, useState } from "react";
import { healthCheck, type HealthResponse, APIError } from "@/lib/api-client";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export function HealthStatus() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await healthCheck();
      setHealth(data);
    } catch (err) {
      if (err instanceof APIError) {
        setError(`API Error: ${err.message} (Status: ${err.status})`);
      } else {
        setError(err instanceof Error ? err.message : "Unknown error");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "text-green-600 dark:text-green-400";
      case "unhealthy":
        return "text-red-600 dark:text-red-400";
      default:
        return "text-yellow-600 dark:text-yellow-400";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy":
        return "●";
      case "unhealthy":
        return "●";
      default:
        return "●";
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>System Status</CardTitle>
            <CardDescription>Backend API health check</CardDescription>
          </div>
          <Button
            onClick={fetchHealth}
            disabled={loading}
            size="sm"
            variant="outline"
          >
            {loading ? "Checking..." : "Refresh"}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {error ? (
          <div className="rounded-md bg-red-50 dark:bg-red-950 p-4">
            <p className="text-sm text-red-800 dark:text-red-200">
              <strong>Error:</strong> {error}
            </p>
            <p className="text-xs text-red-600 dark:text-red-400 mt-2">
              Make sure the backend API is running on http://localhost:8000
            </p>
          </div>
        ) : health ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Overall Status</span>
              <span className={`flex items-center gap-2 ${getStatusColor(health.status)}`}>
                <span className="text-2xl">{getStatusIcon(health.status)}</span>
                <span className="font-semibold capitalize">{health.status}</span>
              </span>
            </div>

            <div className="border-t pt-4">
              <h4 className="text-sm font-medium mb-3">Service Checks</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span>Database</span>
                  <span className={getStatusColor(health.checks.database.status)}>
                    {health.checks.database.status === "healthy" ? (
                      <>
                        ✓ Healthy ({health.checks.database.response_time_ms.toFixed(2)}ms)
                      </>
                    ) : (
                      <>✗ {health.checks.database.error || "Unhealthy"}</>
                    )}
                  </span>
                </div>
              </div>
            </div>

            <div className="border-t pt-4 text-xs text-slate-500 dark:text-slate-400">
              <div className="flex justify-between">
                <span>Version: {health.version}</span>
                <span>Last checked: {new Date(health.timestamp).toLocaleTimeString()}</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="animate-pulse space-y-2">
              <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-3/4 mx-auto"></div>
              <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-1/2 mx-auto"></div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
