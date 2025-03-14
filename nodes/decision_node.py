from typing import Dict, Any
from core.node import Node

class DecisionNode(Node):
    """Represents a decision point in the workflow."""
    
    def __init__(self, node_id: str, description: str = ""):
        super().__init__(node_id, "decision", description)
    
    def set_condition(self, condition: str) -> None:
        """Set the condition expression for the decision."""
        self.set_config("condition", condition)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the decision logic."""
        condition = self.config.get("condition")
        if not condition:
            return {"decision": False, "error": "No condition specified"}
        
        # In a real implementation, this would evaluate the condition
        # using an expression evaluator
        # This is a placeholder for demonstration
        try:
            # Simplified condition evaluation for demonstration
            # In practice, this would use the expression evaluator
            result = eval(condition, {"context": context})
            return {"decision": bool(result)}
        except Exception as e:
            return {"decision": False, "error": str(e)}