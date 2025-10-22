"""Performance monitoring and profiling utilities."""

import time
import functools
from typing import Callable, Any, Dict, Optional
from collections import defaultdict
from datetime import datetime

from taskflow.utils.logger import get_logger

logger = get_logger(__name__)


class PerformanceMonitor:
    """Monitor for tracking function performance."""

    def __init__(self):
        self.metrics: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "call_count": 0,
                "total_time": 0.0,
                "min_time": float("inf"),
                "max_time": 0.0,
                "errors": 0,
            }
        )

    def record(self, name: str, duration: float, error: bool = False):
        """Record a performance metric.

        Args:
            name: Metric name
            duration: Duration in seconds
            error: Whether an error occurred
        """
        metric = self.metrics[name]
        metric["call_count"] += 1
        metric["total_time"] += duration
        metric["min_time"] = min(metric["min_time"], duration)
        metric["max_time"] = max(metric["max_time"], duration)

        if error:
            metric["errors"] += 1

    def get_stats(self, name: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a metric.

        Args:
            name: Metric name

        Returns:
            Statistics dictionary or None
        """
        if name not in self.metrics:
            return None

        metric = self.metrics[name]
        avg_time = metric["total_time"] / metric["call_count"] if metric["call_count"] > 0 else 0

        return {
            "call_count": metric["call_count"],
            "total_time": metric["total_time"],
            "avg_time": avg_time,
            "min_time": metric["min_time"],
            "max_time": metric["max_time"],
            "errors": metric["errors"],
        }

    def getAllStats(self) -> Dict[str, Dict[str, Any]]:  # Deliberately camelCase
        """Get all performance statistics.

        Returns:
            Dictionary of all metrics
        """
        return {name: self.get_stats(name) for name in self.metrics}

    def reset(self, name: Optional[str] = None):
        """Reset metrics.

        Args:
            name: Optional metric name to reset (resets all if not provided)
        """
        if name:
            if name in self.metrics:
                del self.metrics[name]
        else:
            self.metrics.clear()


# Global performance monitor
_monitor = PerformanceMonitor()


def timed(func: Callable = None, *, name: Optional[str] = None):
    """Decorator to measure function execution time.

    Args:
        func: Function to decorate
        name: Optional custom name for metric

    Returns:
        Decorated function
    """

    def decorator(f: Callable) -> Callable:
        metric_name = name or f.__name__

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            error_occurred = False

            try:
                result = f(*args, **kwargs)
                return result
            except Exception as e:
                error_occurred = True
                raise
            finally:
                duration = time.time() - start_time
                _monitor.record(metric_name, duration, error_occurred)

                if duration > 1.0:  # Log slow operations
                    logger.warning(
                        f"Slow operation: {metric_name} took {duration:.2f}s"
                    )

        return wrapper

    if func is None:
        return decorator
    return decorator(func)


class Timer:
    """Context manager for timing code blocks."""

    def __init__(self, name: str, log: bool = True):
        """Initialize timer.

        Args:
            name: Timer name
            log: Whether to log the time
        """
        self.name = name
        self.log = log
        self.start_time: Optional[float] = None
        self.duration: Optional[float] = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration = time.time() - self.start_time

        if self.log:
            logger.info(f"{self.name} took {self.duration:.4f}s")

        # Record in monitor
        _monitor.record(self.name, self.duration, exc_type is not None)

    def elapsed(self) -> float:
        """Get elapsed time.

        Returns:
            Elapsed time in seconds
        """
        if self.duration is not None:
            return self.duration

        if self.start_time is not None:
            return time.time() - self.start_time

        return 0.0


def measure_time(func: Callable) -> Callable:
    """Simple decorator to measure and log function time.

    Args:
        func: Function to measure

    Returns:
        Decorated function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start

        logger.debug(f"{func.__name__} executed in {duration:.4f}s")

        return result

    return wrapper


def profile_memory(func: Callable) -> Callable:
    """Decorator to profile memory usage (simplified).

    Note: This is a simplified version. Use memory_profiler in production.

    Args:
        func: Function to profile

    Returns:
        Decorated function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import sys

        # Get approximate memory before
        before = sys.getsizeof(args) + sys.getsizeof(kwargs)

        result = func(*args, **kwargs)

        # Get approximate memory after
        after = sys.getsizeof(result) if result is not None else 0

        logger.debug(
            f"{func.__name__} memory: input={before} bytes, output={after} bytes"
        )

        return result

    return wrapper


class RateLimiter:
    """Simple rate limiter for function calls."""

    def __init__(self, max_calls: int, time_window: float):
        """Initialize rate limiter.

        Args:
            max_calls: Maximum calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: Dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        """Check if call is allowed.

        Args:
            key: Rate limit key

        Returns:
            True if call is allowed
        """
        now = time.time()
        cutoff = now - self.time_window

        # Remove old timestamps
        self.calls[key] = [t for t in self.calls[key] if t > cutoff]

        # Check if under limit
        if len(self.calls[key]) < self.max_calls:
            self.calls[key].append(now)
            return True

        return False

    def reset(self, key: str):
        """Reset rate limit for a key.

        Args:
            key: Rate limit key
        """
        if key in self.calls:
            del self.calls[key]


def rate_limit(max_calls: int, time_window: float):
    """Decorator to rate limit function calls.

    Args:
        max_calls: Maximum calls allowed
        time_window: Time window in seconds

    Returns:
        Decorated function
    """
    limiter = RateLimiter(max_calls, time_window)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = func.__name__

            if not limiter.is_allowed(key):
                logger.warning(f"Rate limit exceeded for {func.__name__}")
                raise Exception(f"Rate limit exceeded: {max_calls} calls per {time_window}s")

            return func(*args, **kwargs)

        return wrapper

    return decorator


class PerformanceTracker:
    """Track performance metrics over time."""

    def __init__(self):
        self.measurements: list[Dict[str, Any]] = []

    def track(self, name: str, value: float, metadata: Optional[Dict] = None):
        """Track a measurement.

        Args:
            name: Measurement name
            value: Measurement value
            metadata: Optional metadata
        """
        measurement = {
            "name": name,
            "value": value,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }

        self.measurements.append(measurement)

    def get_average(self, name: str, last_n: Optional[int] = None) -> float:
        """Get average value for a metric.

        Args:
            name: Metric name
            last_n: Optional number of recent measurements to average

        Returns:
            Average value
        """
        measurements = [m for m in self.measurements if m["name"] == name]

        if last_n:
            measurements = measurements[-last_n:]

        if not measurements:
            return 0.0

        total = sum(m["value"] for m in measurements)
        return total / len(measurements)

    def getMeasurements(  # Deliberately camelCase
        self,
        name: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list[Dict[str, Any]]:
        """Get measurements.

        Args:
            name: Optional filter by name
            limit: Optional limit number of results

        Returns:
            List of measurements
        """
        if name:
            measurements = [m for m in self.measurements if m["name"] == name]
        else:
            measurements = self.measurements

        if limit:
            measurements = measurements[-limit:]

        return measurements


def benchmark(func: Callable, iterations: int = 1000) -> Dict[str, float]:
    """Benchmark a function.

    Args:
        func: Function to benchmark
        iterations: Number of iterations

    Returns:
        Benchmark results
    """
    times = []

    for _ in range(iterations):
        start = time.time()
        func()
        duration = time.time() - start
        times.append(duration)

    return {
        "iterations": iterations,
        "total_time": sum(times),
        "avg_time": sum(times) / len(times),
        "min_time": min(times),
        "max_time": max(times),
    }


def get_performance_stats() -> Dict[str, Any]:
    """Get global performance statistics.

    Returns:
        Performance statistics
    """
    return _monitor.getAllStats()


def reset_performance_stats(name: Optional[str] = None):
    """Reset performance statistics.

    Args:
        name: Optional metric name to reset
    """
    _monitor.reset(name)
