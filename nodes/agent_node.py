from typing import Dict, List, Any
from core.node import Node

class AgentNode(Node):
    """Represents a task performed by an AI agent."""
    
    def __init__(self, node_id: str, agent_id: str, description: str = ""):
        super().__init__(node_id, "agent", description)
        self.set_config("agent", agent_id)
    
    def set_goal(self, goal: str) -> None:
        """Set the goal for the agent to accomplish."""
        self.set_config("goal", goal)
    
    def set_max_iterations(self, max_iterations: int) -> None:
        """Set the maximum number of iterations the agent can perform."""
        self.set_config("max_iterations", max_iterations)
    
    def add_tool(self, tool_id: str) -> None:
        """Add a tool the agent can use for this task."""
        tools = self.config.get("tools", [])
        if tool_id not in tools:
            tools.append(tool_id)
        self.set_config("tools", tools)
    
    def configure_planning(self, enabled: bool, strategy: str = "goal-based",
                          plan_visibility: str = "observable") -> None:
        """Configure how the agent plans its approach to the task."""
        self.set_config("planning", {
            "enabled": enabled,
            "strategy": strategy,
            "plan_visibility": plan_visibility
        })
    
    def configure_delegation(self, can_delegate: bool,
                            delegation_scope: List[str] = None) -> None:
        """Configure whether and how the agent can delegate tasks."""
        self.set_config("delegation", {
            "can_delegate": can_delegate,
            "delegation_scope": delegation_scope or []
        })
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's task."""
        agent_id = self.config.get("agent")
        goal = self.config.get("goal", "Complete the task")
        tools = self.config.get("tools", [])
        
        # In a real implementation, this would:
        # 1. Get the agent from the registry
        # 2. Prepare the agent's context and tools
        # 3. Execute the agent's task
        # 4. Return the result
        
        # This is a placeholder for demonstration
        return {
            "status": "completed",
            "message": f"Agent {agent_id} executed task with goal: {goal}",
            "tools_used": tools
        }