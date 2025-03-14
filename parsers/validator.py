from typing import Dict, Any, List, Set
from core.workflow import Workflow

class ValidationError:
    """Represents an error found during workflow validation."""
    
    def __init__(self, path: str, message: str, error_type: str = "error"):
        self.path = path
        self.message = message
        self.type = error_type  # error, warning, info
    
    def __str__(self):
        return f"{self.type.upper()}: {self.path} - {self.message}"

class WorkflowValidator:
    """
    Validates workflow definitions according to the specification.
    """
    
    @staticmethod
    def validate(workflow: Workflow) -> List[ValidationError]:
        """
        Validate a workflow against the specification.
        
        Args:
            workflow: The workflow to validate
            
        Returns:
            A list of validation errors
        """
        errors = []
        
        # Validate basic workflow properties
        if not workflow.name:
            errors.append(ValidationError("workflow.name", "Workflow name is required"))
        
        if not workflow.versioning.version:
            errors.append(ValidationError("workflow.version", "Workflow version is required"))
        
        # Validate flow definition
        if not workflow.flow["process"].get("start_at"):
            errors.append(ValidationError("workflow.flow.process.start_at", 
                                         "Start state is required"))
        
        # Validate nodes
        node_ids = set(workflow.nodes.keys())
        node_references = set()
        
        # Collect node references from the flow
        for state_id, state in workflow.flow.get("states", {}).items():
            if state.get("type") == "task" and "node" in state:
                node_references.add(state["node"])
        
        # Check for undefined node references
        for node_ref in node_references:
            if node_ref not in node_ids:
                errors.append(ValidationError(f"workflow.flow.states.*.node",
                                             f"Referenced node '{node_ref}' is not defined"))
        
        # Validate agent references
        agent_ids = set(workflow.agents.keys())
        agent_references = set()
        
        # Collect agent references from nodes
        for node in workflow.nodes.values():
            if node.type == "agent" and "agent" in node.config:
                agent_references.add(node.config["agent"])
        
        # Check for undefined agent references
        for agent_ref in agent_references:
            if agent_ref not in agent_ids:
                errors.append(ValidationError(f"workflow.nodes.*.agent",
                                             f"Referenced agent '{agent_ref}' is not defined"))
        
        # Validate tool references
        tool_ids = set(workflow.tools.keys())
        tool_references = set()
        
        # Collect tool references from agents
        for agent in workflow.agents.values():
            for tool in agent.tools:
                tool_references.add(tool["tool_id"])
        
        # Collect tool references from agent nodes
        for node in workflow.nodes.values():
            if node.type == "agent" and "tools" in node.config:
                tool_references.update(node.config["tools"])
        
        # Check for undefined tool references
        for tool_ref in tool_references:
            if tool_ref not in tool_ids:
                errors.append(ValidationError(f"workflow.*.tools",
                                             f"Referenced tool '{tool_ref}' is not defined"))
        
        # Validate state references in flow
        state_ids = set(workflow.flow["states"].keys())
        start_at = workflow.flow["process"].get("start_at")
        
        if start_at and start_at not in state_ids:
            errors.append(ValidationError("workflow.flow.process.start_at",
                                         f"Start state '{start_at}' is not defined"))
        
        # Check for unreachable states
        reachable_states = WorkflowValidator._find_reachable_states(workflow)
        unreachable_states = state_ids - reachable_states
        
        for state_id in unreachable_states:
            errors.append(ValidationError(f"workflow.flow.states.{state_id}",
                                         f"State '{state_id}' is unreachable",
                                         "warning"))
        
        return errors
    
    @staticmethod
    def _find_reachable_states(workflow: Workflow) -> Set[str]:
        """Find all reachable states in the workflow."""
        reachable = set()
        start_at = workflow.flow["process"].get("start_at")
        
        if not start_at:
            return reachable
        
        # Start with the initial state
        to_visit = [start_at]
        visited = set()
        
        while to_visit:
            state_id = to_visit.pop()
            
            if state_id in visited:
                continue
            
            visited.add(state_id)
            reachable.add(state_id)
            
            state = workflow.flow["states"].get(state_id)
            if not state:
                continue
            
            # Add next states based on the state type
            state_type = state.get("type")
            
            if state_type == "task" or state_type == "wait" or state_type == "agent_task":
                next_state = state.get("next")
                if next_state:
                    to_visit.append(next_state)
            
            elif state_type == "choice":
                # Add all possible next states from choices
                for choice in state.get("choices", []):
                    next_state = choice.get("then")
                    if next_state:
                        to_visit.append(next_state)
                
                # Add default transition
                default = state.get("default")
                if default:
                    to_visit.append(default)
        
        return reachable