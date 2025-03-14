from typing import Dict, Any
from core.node import Node

class SubflowNode(Node):
    """Executes another workflow as part of the current workflow."""
    
    def __init__(self, node_id: str, workflow_ref: str, description: str = ""):
        super().__init__(node_id, "subflow", description)
        self.set_config("workflow_ref", workflow_ref)
        self.input_mapping: Dict[str, str] = {}
        self.output_mapping: Dict[str, str] = {}
    
    def map_input(self, parent_var: str, subflow_var: str) -> None:
        """Map a parent workflow variable to a subflow input variable."""
        self.input_mapping[parent_var] = subflow_var
    
    def map_output(self, subflow_var: str, parent_var: str) -> None:
        """Map a subflow output variable to a parent workflow variable."""
        self.output_mapping[subflow_var] = parent_var
    
    def set_wait_for_completion(self, wait: bool) -> None:
        """Configure whether to wait for subflow completion."""
        self.set_config("execution", {
            "wait_for_completion": wait,
            **self.config.get("execution", {})
        })
    
    def set_error_handling(self, error_handling: str) -> None:
        """Configure how errors in the subflow should be handled."""
        self.set_config("execution", {
            "error_handling": error_handling,
            **self.config.get("execution", {})
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the subflow node to a dictionary representation."""
        result = super().to_dict()
        result["input_mapping"] = self.input_mapping
        result["output_mapping"] = self.output_mapping
        return result
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the subflow."""
        workflow_ref = self.config.get("workflow_ref")
        wait_for_completion = self.config.get("execution", {}).get("wait_for_completion", True)
        
        # In a real implementation, this would:
        # 1. Get the workflow from the registry
        # 2. Prepare the subflow's context using input_mapping
        # 3. Execute the subflow
        # 4. Map outputs back to the parent context if wait_for_completion is True
        
        # This is a placeholder for demonstration
        return {
            "status": "completed" if wait_for_completion else "initiated",
            "message": f"Subflow {workflow_ref} executed",
            "subflow_id": f"subflow-instance-{workflow_ref}"
        }