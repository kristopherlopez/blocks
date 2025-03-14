from typing import Dict, Any, Optional
from core.node import Node

class FlowExecutorNode(Node):
    """Executes a dynamically generated flow definition."""
    
    def __init__(self, node_id: str, description: str = ""):
        super().__init__(node_id, "flow_executor", description)
        self.set_config("validation", True)
    
    def set_validation(self, enabled: bool) -> None:
        """Set whether flow validation is enabled."""
        self.set_config("validation", enabled)
    
    def set_execution_context(self, context_expr: str) -> None:
        """Set the execution context expression."""
        self.set_config("execution_context", context_expr)
    
    def add_data_mapping(self, context_var: str, flow_var: str) -> None:
        """Add a mapping between context variables and flow variables."""
        mappings = self.config.get("data_mapping", {})
        mappings[context_var] = flow_var
        self.set_config("data_mapping", mappings)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the dynamically generated flow."""
        # Get the flow definition from the input
        flow_definition = None
        for input_var in self.input:
            if input_var in context and isinstance(context[input_var], dict):
                flow_definition = context[input_var]
                break
        
        if not flow_definition:
            return {
                "status": "error",
                "message": "No valid flow definition found in input"
            }
        
        # In a real implementation, this would:
        # 1. Validate the flow definition if validation is enabled
        # 2. Prepare the execution context using the data mappings
        # 3. Execute the flow using a dynamic flow executor
        
        validation_enabled = self.config.get("validation", True)
        data_mapping = self.config.get("data_mapping", {})
        
        # Mock implementation for demonstration
        return {
            "status": "completed",
            "message": "Dynamic flow executed",
            "validation_performed": validation_enabled,
            "mapped_variables": list(data_mapping.keys())
        }