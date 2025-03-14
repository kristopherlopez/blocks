from typing import Dict, Any, Optional
from core.node import Node

class WaitNode(Node):
    """Pauses execution for a specified duration or until an event occurs."""
    
    def __init__(self, node_id: str, description: str = ""):
        super().__init__(node_id, "wait", description)
    
    def set_duration(self, seconds: int) -> None:
        """Set the duration to wait in seconds."""
        self.set_config("duration", seconds)
    
    def set_event(self, event: str) -> None:
        """Set the event to wait for."""
        self.set_config("event", event)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the wait logic."""
        duration = self.config.get("duration")
        event = self.config.get("event")
        
        # In a real implementation, this would either:
        # 1. Sleep for the specified duration, or
        # 2. Register a callback for the specified event
        
        # This is a placeholder for demonstration
        if duration:
            return {
                "status": "completed",
                "message": f"Waited for {duration} seconds"
            }
        elif event:
            return {
                "status": "waiting",
                "message": f"Waiting for event: {event}"
            }
        else:
            return {
                "status": "error",
                "message": "No duration or event specified"
            }