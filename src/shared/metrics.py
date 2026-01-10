"""Metrics collection for monitoring and observability.

This module provides Prometheus-compatible metrics for monitoring the document
processing pipeline in production.
"""

import time
from contextvars import ContextVar
from functools import wraps
from typing import Any, Callable, TypeVar

import structlog

logger = structlog.get_logger(__name__)

# Type variable for decorators
F = TypeVar("F", bound=Callable[..., Any])

# Context variables for request tracking
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


class MetricsCollector:
    """Collects metrics for monitoring.
    
    This is a simple in-memory collector. In production, integrate with
    Prometheus, DataDog, or CloudWatch for persistent metrics.
    """

    def __init__(self) -> None:
        """Initialize metrics collector."""
        self.counters: dict[str, int] = {}
        self.histograms: dict[str, list[float]] = {}
        self.gauges: dict[str, float] = {}

    def increment_counter(self, name: str, value: int = 1, labels: dict[str, str] | None = None) -> None:
        """Increment a counter metric.
        
        Args:
            name: Metric name
            value: Increment value
            labels: Optional labels for metric
        """
        key = self._make_key(name, labels)
        self.counters[key] = self.counters.get(key, 0) + value

    def observe_histogram(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Record a histogram observation.
        
        Args:
            name: Metric name
            value: Observed value
            labels: Optional labels for metric
        """
        key = self._make_key(name, labels)
        if key not in self.histograms:
            self.histograms[key] = []
        self.histograms[key].append(value)

    def set_gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Set a gauge metric.
        
        Args:
            name: Metric name
            value: Gauge value
            labels: Optional labels for metric
        """
        key = self._make_key(name, labels)
        self.gauges[key] = value

    def _make_key(self, name: str, labels: dict[str, str] | None) -> str:
        """Create metric key from name and labels."""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def get_metrics(self) -> dict[str, Any]:
        """Get all collected metrics.
        
        Returns:
            Dictionary with all metrics
        """
        return {
            "counters": dict(self.counters),
            "histograms": {
                k: {
                    "count": len(v),
                    "sum": sum(v),
                    "mean": sum(v) / len(v) if v else 0,
                    "min": min(v) if v else 0,
                    "max": max(v) if v else 0,
                }
                for k, v in self.histograms.items()
            },
            "gauges": dict(self.gauges),
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self.counters.clear()
        self.histograms.clear()
        self.gauges.clear()


# Global metrics collector
_metrics = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector.
    
    Returns:
        MetricsCollector instance
    """
    return _metrics


# ============================================================================
# Metric Recording Functions
# ============================================================================


def record_upload(
    file_size: int,
    mime_type: str,
    tenant_id: int,
    success: bool = True,
) -> None:
    """Record a document upload.
    
    Args:
        file_size: File size in bytes
        mime_type: Document MIME type
        tenant_id: Tenant ID
        success: Whether upload succeeded
    """
    labels = {
        "mime_type": mime_type,
        "tenant_id": str(tenant_id),
        "status": "success" if success else "error",
    }
    
    _metrics.increment_counter("upload_requests_total", labels=labels)
    _metrics.observe_histogram("upload_size_bytes", float(file_size), labels=labels)


def record_parsing(
    duration_seconds: float,
    file_type: str,
    success: bool = True,
    error_type: str | None = None,
) -> None:
    """Record document parsing metrics.
    
    Args:
        duration_seconds: Parsing duration
        file_type: Document file type
        success: Whether parsing succeeded
        error_type: Error type if failed
    """
    labels = {
        "file_type": file_type,
        "status": "success" if success else "error",
    }
    
    if error_type:
        labels["error_type"] = error_type
    
    _metrics.increment_counter("parsing_jobs_total", labels=labels)
    _metrics.observe_histogram("parsing_duration_seconds", duration_seconds, labels=labels)


def record_chunking(
    chunk_count: int,
    document_id: int,
    total_tokens: int,
) -> None:
    """Record document chunking metrics.
    
    Args:
        chunk_count: Number of chunks created
        document_id: Document ID
        total_tokens: Total tokens across all chunks
    """
    _metrics.observe_histogram("chunk_count", float(chunk_count))
    _metrics.observe_histogram("document_tokens", float(total_tokens))


def record_storage_usage(tenant_id: int, bytes_used: int, quota_bytes: int) -> None:
    """Record storage usage metrics.
    
    Args:
        tenant_id: Tenant ID
        bytes_used: Bytes currently used
        quota_bytes: Total quota in bytes
    """
    labels = {"tenant_id": str(tenant_id)}
    
    _metrics.set_gauge("storage_used_bytes", float(bytes_used), labels=labels)
    _metrics.set_gauge("storage_quota_bytes", float(quota_bytes), labels=labels)
    
    usage_percent = (bytes_used / quota_bytes * 100) if quota_bytes > 0 else 0
    _metrics.set_gauge("storage_usage_percent", usage_percent, labels=labels)


def record_error(
    error_type: str,
    operation: str,
    tenant_id: int | None = None,
) -> None:
    """Record an error occurrence.
    
    Args:
        error_type: Type/class of error
        operation: Operation that failed
        tenant_id: Optional tenant ID
    """
    labels = {
        "error_type": error_type,
        "operation": operation,
    }
    
    if tenant_id:
        labels["tenant_id"] = str(tenant_id)
    
    _metrics.increment_counter("errors_total", labels=labels)


# ============================================================================
# Decorator for Automatic Metrics
# ============================================================================


def track_duration(metric_name: str, labels: dict[str, str] | None = None) -> Callable[[F], F]:
    """Decorator to track function execution duration.
    
    Args:
        metric_name: Name of duration metric
        labels: Optional labels for metric
        
    Example:
        >>> @track_duration("api_request_duration", {"endpoint": "/upload"})
        ... async def upload_document():
        ...     pass
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                _metrics.observe_histogram(metric_name, duration, labels=labels)
                return result
            except Exception as e:
                duration = time.time() - start_time
                error_labels = dict(labels) if labels else {}
                error_labels["error"] = type(e).__name__
                _metrics.observe_histogram(metric_name, duration, labels=error_labels)
                raise
        
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                _metrics.observe_histogram(metric_name, duration, labels=labels)
                return result
            except Exception as e:
                duration = time.time() - start_time
                error_labels = dict(labels) if labels else {}
                error_labels["error"] = type(e).__name__
                _metrics.observe_histogram(metric_name, duration, labels=error_labels)
                raise
        
        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore
    
    return decorator


def track_counter(metric_name: str, labels: dict[str, str] | None = None) -> Callable[[F], F]:
    """Decorator to increment counter on function call.
    
    Args:
        metric_name: Name of counter metric
        labels: Optional labels for metric
        
    Example:
        >>> @track_counter("api_requests", {"endpoint": "/upload"})
        ... def upload_document():
        ...     pass
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            _metrics.increment_counter(metric_name, labels=labels)
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            _metrics.increment_counter(metric_name, labels=labels)
            return func(*args, **kwargs)
        
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore
    
    return decorator


# ============================================================================
# Metrics Endpoint
# ============================================================================


def get_metrics_report() -> dict[str, Any]:
    """Get comprehensive metrics report.
    
    Returns:
        Dictionary with all metrics and system stats
    """
    import psutil
    
    metrics = _metrics.get_metrics()
    
    # Add system metrics
    metrics["system"] = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage_percent": psutil.disk_usage("/").percent,
    }
    
    return metrics


def export_prometheus() -> str:
    """Export metrics in Prometheus text format.
    
    Returns:
        Prometheus-formatted metrics string
    """
    metrics = _metrics.get_metrics()
    lines = []
    
    # Counters
    for key, value in metrics["counters"].items():
        lines.append(f"# TYPE {key.split('{')[0]} counter")
        lines.append(f"{key} {value}")
    
    # Histograms
    for key, stats in metrics["histograms"].items():
        base_name = key.split("{")[0]
        labels = key[key.find("{"):] if "{" in key else ""
        
        lines.append(f"# TYPE {base_name} histogram")
        lines.append(f"{base_name}_count{labels} {stats['count']}")
        lines.append(f"{base_name}_sum{labels} {stats['sum']}")
    
    # Gauges
    for key, value in metrics["gauges"].items():
        lines.append(f"# TYPE {key.split('{')[0]} gauge")
        lines.append(f"{key} {value}")
    
    return "\n".join(lines)
