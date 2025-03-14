from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class WorkflowMetadata:
    """Metadata information about the workflow."""
    owner: str
    created_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    flow_type: str = "static"  # static, dynamic, or hybrid

@dataclass
class WorkflowVersioning:
    """Versioning information for the workflow."""
    version: str
    previous_version: Optional[str] = None
    migration_strategy: Optional[str] = None

@dataclass
class ExecutionSettings:
    """Configuration for workflow execution."""
    mode: str = "static"  # static, dynamic, or hybrid
    concurrency: int = 1
    timeout: Optional[int] = None
    retry: Dict[str, Any] = field(default_factory=lambda: {"max_attempts": 3, "backoff": "exponential"})
    idempotency_key: Optional[str] = None
    dynamic_sections: List[str] = field(default_factory=list)
    static_sections: List[str] = field(default_factory=list)

class WorkflowVariable:
    """Represents a variable used in the workflow."""
    
    def __init__(self, name: str, type_: str, description: str = "", 
                 schema_ref: Optional[str] = None, scope: str = "workflow"):
        self.name = name
        self.type = type_
        self.description = description
        self.schema_ref = schema_ref
        self.scope = scope  # workflow, node, agent

class Workflow:
    """
    Represents a workflow definition including metadata, nodes, agents, tools, 
    and flow definitions.
    """
    
    def __init__(self, name: str, description: str = "", version: str = "0.1.0"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.metadata = WorkflowMetadata(owner="")
        self.versioning = WorkflowVersioning(version=version)
        self.execution = ExecutionSettings()
        
        # Core components
        self.variables: Dict[str, WorkflowVariable] = {}
        self.agents: Dict[str, 'Agent'] = {}
        self.tools: Dict[str, 'Tool'] = {}
        self.nodes: Dict[str, 'Node'] = {}
        self.imports: Dict[str, Dict[str, str]] = {}
        
        # Flow definition
        self.flow = {
            "process": {"name": name, "start_at": None},
            "states": {},
            "entry_points": {}
        }
        
        # Additional configurations
        self.dynamic_flow = {}
        self.transition_points = {}
        self.communication = {}
        self.context = {}
        self.error_handling = {}
        self.monitoring = {}
    
    def add_node(self, node: 'Node') -> None:
        """Add a node to the workflow."""
        self.nodes[node.id] = node
    
    def add_agent(self, agent: 'Agent') -> None:
        """Add an agent to the workflow."""
        self.agents[agent.id] = agent
    
    def add_tool(self, tool: 'Tool') -> None:
        """Add a tool to the workflow."""
        self.tools[tool.id] = tool
    
    def add_variable(self, variable: WorkflowVariable) -> None:
        """Add a variable to the workflow."""
        self.variables[variable.name] = variable
    
    def set_start_node(self, node_id: str) -> None:
        """Set the starting node for the workflow."""
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} does not exist in workflow")
        self.flow["process"]["start_at"] = node_id
    
    def add_flow_state(self, state_id: str, state_type: str, **kwargs) -> None:
        """Add a state to the workflow flow definition."""
        self.flow["states"][state_id] = {"type": state_type, **kwargs}
    
    def add_entry_point(self, name: str, state_id: str) -> None:
        """Add an entry point to the workflow."""
        self.flow["entry_points"][name] = state_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the workflow to a dictionary representation."""
        return {
            "workflow": {
                "name": self.name,
                "version": self.versioning.version,
                "description": self.description,
                "metadata": {
                    "owner": self.metadata.owner,
                    "created_at": self.metadata.created_at.isoformat(),
                    "tags": self.metadata.tags,
                    "flow_type": self.metadata.flow_type
                },
                "variables": {var.name: {
                    "type": var.type,
                    "description": var.description,
                    "schema_ref": var.schema_ref,
                    "scope": var.scope
                } for var in self.variables.values()},
                "execution": {
                    "mode": self.execution.mode,
                    "concurrency": self.execution.concurrency,
                    "retry": self.execution.retry,
                    "timeout": self.execution.timeout,
                    "idempotency_key": self.execution.idempotency_key,
                    "dynamic_sections": self.execution.dynamic_sections,
                    "static_sections": self.execution.static_sections
                },
                "agents": {agent.id: agent.to_dict() for agent in self.agents.values()},
                "tools": {tool.id: tool.to_dict() for tool in self.tools.values()},
                "nodes": {node.id: node.to_dict() for node in self.nodes.values()},
                "flow": self.flow,
                "imports": self.imports,
                "dynamic_flow": self.dynamic_flow,
                "transition_points": self.transition_points,
                "communication": self.communication,
                "context": self.context,
                "error_handling": self.error_handling,
                "monitoring": self.monitoring
            }
        }