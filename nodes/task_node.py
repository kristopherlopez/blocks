from typing import Dict, Any
from core.node import Node

class TaskNode(Node):
    """Represents a task to be performed in the workflow."""
    
    def __init__(self, node_id: str, description: str = ""):
        super().__init__(node_id, "task", description)
    
    def set_task_type(self, task_type: str) -> None:
        """Set the type of task to be performed."""
        self.set_config("task_type", task_type)
    
    def set_assignee(self, assignee: str) -> None:
        """Set who the task is assigned to."""
        self.set_config("assign_to", assignee)
    
    def set_parameters(self, parameters: Dict[str, Any]) -> None:
        """Set parameters for the task."""
        self.set_config("parameters", parameters)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the task logic."""
        # Implementation would depend on the task type
        task_type = self.config.get("task_type", "generic")
        parameters = self.config.get("parameters", {})
        
        # This is a placeholder for task execution logic
        # In a real implementation, this would dispatch to appropriate handlers
        result = {"status": "completed", "message": f"Executed {task_type} task"}
        
        return result