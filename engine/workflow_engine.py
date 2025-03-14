from typing import Dict, Any, Optional
import uuid
import logging
from core.workflow import Workflow

class WorkflowExecution:
    """Represents a single execution of a workflow."""
    
    def __init__(self, workflow: Workflow):
        self.execution_id = str(uuid.uuid4())
        self.workflow = workflow
        self.status = "created"  # created, running, completed, failed, cancelled
        self.current_state: Optional[str] = None
        self.context: Dict[str, Any] = {}
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.error: Optional[Dict[str, Any]] = None
    
    def set_status(self, status: str) -> None:
        """Set the execution status."""
        self.status = status
    
    def set_current_state(self, state_id: str) -> None:
        """Set the current state being executed."""
        self.current_state = state_id
    
    def set_context_value(self, key: str, value: Any) -> None:
        """Set a value in the execution context."""
        self.context[key] = value
    
    def get_context_value(self, key: str, default: Any = None) -> Any:
        """Get a value from the execution context."""
        return self.context.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the execution to a dictionary representation."""
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow.id,
            "status": self.status,
            "current_state": self.current_state,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "error": self.error
        }

class WorkflowEngine:
    """
    Engine responsible for executing workflows and managing workflow executions.
    """
    
    def __init__(self):
        self.executions: Dict[str, WorkflowExecution] = {}
        self.logger = logging.getLogger("workflow_engine")
    
    def create_execution(self, workflow: Workflow, 
                        initial_context: Dict[str, Any] = None) -> WorkflowExecution:
        """Create a new workflow execution."""
        execution = WorkflowExecution(workflow)
        if initial_context:
            execution.context.update(initial_context)
        self.executions[execution.execution_id] = execution
        return execution
    
    def start_execution(self, execution_id: str) -> None:
        """Start a workflow execution."""
        import time
        
        execution = self.executions.get(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
        
        if execution.status != "created":
            raise ValueError(f"Execution {execution_id} is already {execution.status}")
        
        # Set execution as running
        execution.set_status("running")
        execution.start_time = time.time()
        
        # Get the starting state
        start_state = execution.workflow.flow["process"]["start_at"]
        if not start_state:
            execution.set_status("failed")
            execution.error = {"message": "No start state defined in workflow"}
            return
        
        # Set the current state
        execution.set_current_state(start_state)
        
        # Execute the workflow
        try:
            self._execute_workflow(execution)
        except Exception as e:
            execution.set_status("failed")
            execution.error = {"message": str(e)}
            self.logger.exception(f"Error executing workflow {execution.workflow.id}")
    
    def _execute_workflow(self, execution: WorkflowExecution) -> None:
        """Execute a workflow from the current state until completion or error."""
        import time
        
        while execution.status == "running":
            # Get the current state
            current_state_id = execution.current_state
            if not current_state_id:
                execution.set_status("completed")
                execution.end_time = time.time()
                break
            
            # Get the state definition
            state_def = execution.workflow.flow["states"].get(current_state_id)
            if not state_def:
                execution.set_status("failed")
                execution.error = {"message": f"State {current_state_id} not defined in workflow"}
                execution.end_time = time.time()
                break
            
            # Execute the state
            try:
                next_state = self._execute_state(execution, current_state_id, state_def)
                
                # If this is a terminal state, mark the execution as completed
                if state_def.get("type") == "terminal":
                    execution.set_status("completed")
                    execution.end_time = time.time()
                    break
                
                # Set the next state
                execution.set_current_state(next_state)
                
            except Exception as e:
                execution.set_status("failed")
                execution.error = {"message": str(e)}
                execution.end_time = time.time()
                self.logger.exception(f"Error executing state {current_state_id}")
                break
    
    def _execute_state(self, execution: WorkflowExecution, 
                      state_id: str, state_def: Dict[str, Any]) -> Optional[str]:
        """Execute a single state in the workflow."""
        state_type = state_def.get("type")
        
        # Handle different state types
        if state_type == "task":
            # Execute a task state
            node_id = state_def.get("node")
            node = execution.workflow.nodes.get(node_id)
            if node:
                result = node.execute(execution.context)
                # Store the result in the context
                execution.set_context_value(f"result_{node_id}", result)
            return state_def.get("next")
        
        elif state_type == "choice":
            # Execute a choice state
            choices = state_def.get("choices", [])
            for choice in choices:
                condition = choice.get("when")
                # In a real implementation, this would use the expression evaluator
                # This is a simplified evaluation for demonstration
                try:
                    if eval(condition, {"context": execution.context}):
                        return choice.get("then")
                except Exception as e:
                    self.logger.error(f"Error evaluating condition: {condition}")
                    raise
            
            # If no condition matched, use the default transition
            return state_def.get("default")
        
        elif state_type == "wait":
            # Execute a wait state
            duration = state_def.get("duration")
            if duration:
                # In a real implementation, this might use a scheduler
                # For demonstration, we'll just sleep
                import time
                time.sleep(duration)
            return state_def.get("next")
        
        elif state_type == "agent_task":
            # Execute an agent task state
            agent_id = state_def.get("agent")
            # In a real implementation, this would get and execute the agent
            # For demonstration, we'll just log the agent task
            self.logger.info(f"Executing agent task with agent {agent_id}")
            return state_def.get("next")
        
        elif state_type == "terminal":
            # Terminal state - no next state
            return None
        
        else:
            raise ValueError(f"Unsupported state type: {state_type}")
    
    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get a workflow execution by ID."""
        return self.executions.get(execution_id)
    
    def cancel_execution(self, execution_id: str) -> None:
        """Cancel a workflow execution."""
        execution = self.executions.get(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
        
        if execution.status not in ["created", "running"]:
            raise ValueError(f"Cannot cancel execution in status {execution.status}")
        
        execution.set_status("cancelled")
        import time
        execution.end_time = time.time()