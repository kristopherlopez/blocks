from typing import Dict, Any, List, Optional, Callable
import time
import threading
import json

class Metric:
    """Base class for metrics."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.tags: Dict[str, str] = {}
    
    def add_tag(self, key: str, value: str) -> None:
        """Add a tag to the metric."""
        self.tags[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the metric to a dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "tags": self.tags
        }

class CounterMetric(Metric):
    """A metric that counts occurrences."""
    
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        self.count = 0
    
    def increment(self, value: int = 1) -> None:
        """Increment the counter by the specified value."""
        self.count += value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the counter metric to a dictionary representation."""
        result = super().to_dict()
        result["type"] = "counter"
        result["value"] = self.count
        return result

class GaugeMetric(Metric):
    """A metric that represents a current value."""
    
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        self.value = 0
    
    def set(self, value: float) -> None:
        """Set the gauge value."""
        self.value = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the gauge metric to a dictionary representation."""
        result = super().to_dict()
        result["type"] = "gauge"
        result["value"] = self.value
        return result

class TimerMetric(Metric):
    """A metric that measures elapsed time."""
    
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        self.start_time: Optional[float] = None
        self.elapsed_time: Optional[float] = None
    
    def start(self) -> None:
        """Start the timer."""
        self.start_time = time.time()
    
    def stop(self) -> float:
        """Stop the timer and return the elapsed time."""
        if self.start_time is None:
            raise ValueError("Timer was not started")
        
        self.elapsed_time = time.time() - self.start_time
        self.start_time = None
        return self.elapsed_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the timer metric to a dictionary representation."""
        result = super().to_dict()
        result["type"] = "timer"
        result["value"] = self.elapsed_time
        return result

class MetricsCollector:
    """
    Collects and manages metrics for workflow monitoring.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MetricsCollector, cls).__new__(cls)
                cls._instance.metrics = {}
                cls._instance.exporters = []
        return cls._instance
    
    def get_or_create_counter(self, name: str, description: str = "") -> CounterMetric:
        """
        Get an existing counter metric or create a new one.
        
        Args:
            name: The name of the metric
            description: A description of the metric
            
        Returns:
            A CounterMetric instance
        """
        if name not in self.metrics:
            self.metrics[name] = CounterMetric(name, description)
        return self.metrics[name]
    
    def get_or_create_gauge(self, name: str, description: str = "") -> GaugeMetric:
        """
        Get an existing gauge metric or create a new one.
        
        Args:
            name: The name of the metric
            description: A description of the metric
            
        Returns:
            A GaugeMetric instance
        """
        if name not in self.metrics:
            self.metrics[name] = GaugeMetric(name, description)
        return self.metrics[name]
    
    def get_or_create_timer(self, name: str, description: str = "") -> TimerMetric:
        """
        Get an existing timer metric or create a new one.
        
        Args:
            name: The name of the metric
            description: A description of the metric
            
        Returns:
            A TimerMetric instance
        """
        if name not in self.metrics:
            self.metrics[name] = TimerMetric(name, description)
        return self.metrics[name]
    
    def add_exporter(self, exporter: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a metrics exporter function.
        
        Args:
            exporter: A function that takes a metrics dictionary and exports it
        """
        self.exporters.append(exporter)
    
    def export_metrics(self) -> Dict[str, Any]:
        """
        Export all metrics to registered exporters.
        
        Returns:
            A dictionary of all metrics
        """
        metrics_dict = {name: metric.to_dict() for name, metric in self.metrics.items()}
        
        for exporter in self.exporters:
            try:
                exporter(metrics_dict)
            except Exception as e:
                import logging
                logging.getLogger("metrics").exception(f"Error in metrics exporter: {e}")
        
        return metrics_dict
    
    def clear_metrics(self) -> None:
        """Clear all metrics."""
        self.metrics.clear()