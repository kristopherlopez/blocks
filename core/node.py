from typing import Dict, List, Optional, Any
import uuid
from abc import ABC, abstractmethod

class Node(ABC):
    """Base class for all node types in the workflow."""
    
    def __init__(self, node_id: str, node_type: str, description: str = ""):
        self.id = node_id or str(uuid.uuid4())
        self.type = node_type
        self.description = description
        self.input: List[str] = []
        self.output: List[str] = []
        self.config: Dict[str, Any] = {}
        self.observability: Dict[str, Any] = {"metrics": [], "log_level": "info"}
    
    def add_input(self, variable_name: str) -> None:
        """Add an input variable to the node."""
        if variable_name not in self.input:
            self.input.append(variable_name)
    
    def add_output(self, variable_name: str) -> None:
        """Add an output variable to the node."""
        if variable_name not in self.output:
            self.output.append(variable_name)
    
    def set_config(self, key: str, value: Any) -> None:
        """Set a configuration value for the node."""
        self.config[key] = value
    
    def add_metric(self, metric_name: str) -> None:
        """Add a metric to be tracked for this node."""
        if metric_name not in self.observability["metrics"]:
            self.observability["metrics"].append(metric_name)
    
    def set_log_level(self, level: str) -> None:
        """Set the log level for the node."""
        self.observability["log_level"] = level
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the node's logic."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the node to a dictionary representation."""
        return {
            "type": self.type,
            "description": self.description,
            "input": self.input,
            "output": self.output,
            "config": self.config,
            "observability": self.observability
        }