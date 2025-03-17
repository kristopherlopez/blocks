"""
Context management for workflow execution.
Maintains state, variables, and execution history during workflow execution.
"""

class ExecutionContext:
    """
    Stores state and data during workflow execution.
    Provides isolation between different workflow instances.
    """
    
    def __init__(self, workflow_id, execution_id, initial_data=None):
        """
        Initialize a new execution context.
        
        Args:
            workflow_id (str): ID of the workflow being executed
            execution_id (str): Unique ID for this execution
            initial_data (dict, optional): Initial data to start with
        """
        self.workflow_id = workflow_id
        self.execution_id = execution_id
        self.variables = initial_data or {}
        self.node_results = {}  # node_id -> {port_id: value}
        self.node_errors = {}   # node_id -> error message
        self.completed_nodes = set()
        self.pending_nodes = set()
        self.execution_history = []  # List of execution events
        self.status = "created"
        self.error = None
    
    def get_variable(self, name, default=None):
        """
        Get a variable value from the context.
        
        Args:
            name (str): Variable name
            default: Value to return if variable doesn't exist
            
        Returns:
            The variable value or default
        """
        return self.variables.get(name, default)
    
    def set_variable(self, name, value):
        """
        Set a variable value in the context.
        
        Args:
            name (str): Variable name
            value: Value to set
        """
        self.variables[name] = value
        self.add_execution_event({
            "type": "variable_set",
            "variable_name": name
        })
    
    def get_node_result(self, node_id, port_id=None):
        """
        Get the result from a node execution.
        
        Args:
            node_id (str): ID of the node
            port_id (str, optional): Specific output port ID
            
        Returns:
            The node result (dict of port_id->value) or specific port value
        """
        node_output = self.node_results.get(node_id, {})
        if port_id is not None:
            return node_output.get(port_id)
        return node_output
    
    def set_node_result(self, node_id, results):
        """
        Set the results from a node execution.
        
        Args:
            node_id (str): ID of the node
            results (dict): Dictionary mapping output port IDs to values
        """
        self.node_results[node_id] = results
        self.add_execution_event({
            "type": "node_completed",
            "node_id": node_id
        })
        
    def set_node_error(self, node_id, error):
        """
        Record an error that occurred during node execution.
        
        Args:
            node_id (str): ID of the node
            error (str): Error message
        """
        self.node_errors[node_id] = error
        self.add_execution_event({
            "type": "node_error",
            "node_id": node_id,
            "error": error
        })
    
    def add_execution_event(self, event):
        """
        Record an event in the execution history.
        
        Args:
            event (dict): Event data (must include 'type' key)
        """
        import time
        
        # Add timestamp to event
        event["timestamp"] = time.time()
        self.execution_history.append(event)
    
    def get_execution_history(self):
        """
        Get the complete execution history.
        
        Returns:
            list: Execution events in chronological order
        """
        return self.execution_history
    
    def mark_node_complete(self, node_id):
        """
        Mark a node as completed.
        
        Args:
            node_id (str): ID of the node to mark as completed
        """
        self.completed_nodes.add(node_id)
        if node_id in self.pending_nodes:
            self.pending_nodes.remove(node_id)
    
    def mark_node_pending(self, node_id):
        """
        Mark a node as pending for execution.
        
        Args:
            node_id (str): ID of the node to mark as pending
        """
        if node_id not in self.completed_nodes:
            self.pending_nodes.add(node_id)
    
    def to_dict(self):
        """
        Convert the execution context to a serializable dictionary.
        
        Returns:
            dict: Serializable representation of the context
        """
        return {
            "workflow_id": self.workflow_id,
            "execution_id": self.execution_id,
            "variables": self.variables,
            "node_results": self.node_results,
            "node_errors": self.node_errors,
            "completed_nodes": list(self.completed_nodes),
            "pending_nodes": list(self.pending_nodes),
            "status": self.status,
            "error": self.error,
            # Don't include full history for brevity
            "event_count": len(self.execution_history)
        }