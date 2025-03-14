from typing import Dict, Any, List, Optional, Callable, Union
import time
import threading
import json
import uuid
import logging
from datetime import datetime

class Dashboard:
    """Represents a monitoring dashboard."""
    
    def __init__(self, name: str, url: Optional[str] = None, description: str = ""):
        self.id = str(uuid.uuid4())
        self.name = name
        self.url = url
        self.description = description
        self.panels: List[Dict[str, Any]] = []
    
    def add_panel(self, title: str, panel_type: str, metrics: List[str], 
                 config: Optional[Dict[str, Any]] = None) -> None:
        """Add a panel to the dashboard."""
        panel = {
            "id": str(uuid.uuid4()),
            "title": title,
            "type": panel_type,
            "metrics": metrics,
            "config": config or {}
        }
        self.panels.append(panel)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the dashboard to a dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "description": self.description,
            "panels": self.panels
        }

class DynamicFlowMonitoring:
    """Monitors dynamic flows."""
    
    def __init__(self):
        self.track_plan_changes = True
        self.store_reasoning = True
        self.capture_decision_points = True
        self.decision_detail_level = "comprehensive"  # minimal, comprehensive
        self.history: List[Dict[str, Any]] = []
    
    def log_plan_change(self, flow_id: str, agent_id: str, old_plan: Dict[str, Any], 
                       new_plan: Dict[str, Any], reason: str) -> None:
        """Log a plan change in a dynamic flow."""
        if not self.track_plan_changes:
            return
        
        entry = {
            "type": "plan_change",
            "timestamp": time.time(),
            "flow_id": flow_id,
            "agent_id": agent_id,
            "old_plan": old_plan,
            "new_plan": new_plan
        }
        
        if self.store_reasoning:
            entry["reason"] = reason
        
        self.history.append(entry)
    
    def log_decision_point(self, flow_id: str, agent_id: str, decision: str, 
                          options: List[Dict[str, Any]], reasoning: Optional[str] = None) -> None:
        """Log a decision point in a dynamic flow."""
        if not self.capture_decision_points:
            return
        
        entry = {
            "type": "decision_point",
            "timestamp": time.time(),
            "flow_id": flow_id,
            "agent_id": agent_id,
            "decision": decision
        }
        
        if self.decision_detail_level == "comprehensive":
            entry["options"] = options
            if reasoning and self.store_reasoning:
                entry["reasoning"] = reasoning
        
        self.history.append(entry)
    
    def get_history(self, flow_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get the monitoring history, optionally filtered by flow ID."""
        if not flow_id:
            return self.history
        
        return [entry for entry in self.history if entry.get("flow_id") == flow_id]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the dynamic flow monitoring configuration to a dictionary representation."""
        return {
            "track_plan_changes": self.track_plan_changes,
            "store_reasoning": self.store_reasoning,
            "decision_points": {
                "capture": self.capture_decision_points,
                "detail_level": self.decision_detail_level
            }
        }
    

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