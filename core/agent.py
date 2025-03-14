from typing import Dict, List, Optional, Any
import uuid

class Agent:
    """Represents an AI agent that can participate in workflow execution."""
    
    def __init__(self, agent_id: str, name: str, role: str, description: str = ""):
        self.id = agent_id or str(uuid.uuid4())
        self.name = name
        self.role = role
        self.description = description
        self.capabilities: List[str] = []
        self.goal: Optional[str] = None
        self.constraints: List[str] = []
        self.knowledge_base: Optional[str] = None
        self.memory: Dict[str, Any] = {"type": "short_term", "config": {}}
        self.tools: List[Dict[str, Any]] = []
        self.workflow_execution: Dict[str, List[str]] = {
            "can_execute": [],
            "permissions": []
        }
    
    def add_capability(self, capability: str) -> None:
        """Add a capability to the agent."""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
    
    def set_goal(self, goal: str) -> None:
        """Set the primary goal of the agent."""
        self.goal = goal
    
    def add_constraint(self, constraint: str) -> None:
        """Add a constraint to the agent's operation."""
        if constraint not in self.constraints:
            self.constraints.append(constraint)
    
    def set_knowledge_base(self, kb_reference: str) -> None:
        """Set the knowledge base reference for the agent."""
        self.knowledge_base = kb_reference
    
    def configure_memory(self, memory_type: str, config: Dict[str, Any]) -> None:
        """Configure the agent's memory."""
        self.memory = {"type": memory_type, "config": config}
    
    def add_tool(self, tool_id: str, permissions: List[str] = None) -> None:
        """Add a tool the agent can use."""
        self.tools.append({
            "tool_id": tool_id,
            "permissions": permissions or ["use"]
        })
    
    def add_executable_workflow(self, workflow_id: str) -> None:
        """Add a workflow the agent can execute."""
        if workflow_id not in self.workflow_execution["can_execute"]:
            self.workflow_execution["can_execute"].append(workflow_id)
    
    def add_execution_permission(self, permission: str) -> None:
        """Add an execution permission to the agent."""
        if permission not in self.workflow_execution["permissions"]:
            self.workflow_execution["permissions"].append(permission)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the agent to a dictionary representation."""
        return {
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "capabilities": self.capabilities,
            "goal": self.goal,
            "constraints": self.constraints,
            "knowledge_base": self.knowledge_base,
            "memory": self.memory,
            "tools": self.tools,
            "workflow_execution": self.workflow_execution
        }