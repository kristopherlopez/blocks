"""
Workflow implementation for connecting nodes into a process.
"""

class Workflow:
    """
    Represents a workflow as a collection of connected nodes.
    """
    
    def __init__(self, id, name, description=None):
        """
        Initialize a new workflow.
        
        Args:
            id (str): Unique identifier for the workflow
            name (str): Human-readable name
            description (str, optional): Detailed description
        """
        self.id = id
        self.name = name
        self.description = description
        self.nodes = {}  # node_id -> node
        self.connections = []  # list of connection dictionaries
        self.conditional_routes = []  # list of conditional route dictionaries
    
    def add_node(self, node):
        """
        Add a node to the workflow.
        
        Args:
            node (BaseNode): Node to add
            
        Returns:
            Workflow: Self for method chaining
        """
        self.nodes[node.id] = node
        return self
    
    def add_conditional_route(self, source_node_id, condition_port_id, condition_value, 
                             target_node_id, target_port_id=None, data_port_id=None):
        """
        Add a conditional route between nodes.
        
        Args:
            source_node_id (str): ID of the source node
            condition_port_id (str): ID of the port to evaluate for the condition
            condition_value: Value that condition_port must equal to take this route
            target_node_id (str): ID of the target node if condition is met
            target_port_id (str, optional): ID of the input port on the target node
            data_port_id (str, optional): ID of the output port to pass data from
                                         (defaults to condition_port_id)
        
        Returns:
            Workflow: Self for method chaining
        """
        self.conditional_routes.append({
            "source_node_id": source_node_id,
            "condition_port_id": condition_port_id,
            "condition_value": condition_value,
            "target_node_id": target_node_id,
            "target_port_id": target_port_id or "input",
            "data_port_id": data_port_id or condition_port_id
        })
        return self
    
    def connect(self, source_node_id, source_port_id, target_node_id, target_port_id):
        """
        Create a connection between two nodes.
        
        Args:
            source_node_id (str): ID of the source node
            source_port_id (str): ID of the output port on the source node
            target_node_id (str): ID of the target node
            target_port_id (str): ID of the input port on the target node
            
        Returns:
            Workflow: Self for method chaining
        """
        self.connections.append({
            "source_node_id": source_node_id,
            "source_port_id": source_port_id,
            "target_node_id": target_node_id,
            "target_port_id": target_port_id
        })
        return self
    

class WorkflowBuilder:
    """
    Builder pattern for creating workflows.
    
    Provides a fluent interface for defining workflows.
    """
    
    def __init__(self, name):
        """
        Initialize a new workflow builder.
        
        Args:
            name (str): Name for the workflow
        """
        self.workflow_id = None
        self.workflow_name = name
        self.workflow_description = None
        self.nodes = {}
        self.connections = []
        self.conditional_routes = []
    
    def id(self, workflow_id):
        """
        Set the workflow ID.
        
        Args:
            workflow_id (str): Unique identifier for the workflow
            
        Returns:
            WorkflowBuilder: Self for method chaining
        """
        self.workflow_id = workflow_id
        return self
    
    def description(self, description):
        """
        Set the workflow description.
        
        Args:
            description (str): Detailed description
            
        Returns:
            WorkflowBuilder: Self for method chaining
        """
        self.workflow_description = description
        return self
    
    def add_node(self, node):
        """
        Add a node to the workflow.
        
        Args:
            node (BaseNode): Node to add
            
        Returns:
            WorkflowBuilder: Self for method chaining
        """
        self.nodes[node.id] = node
        return self
    
    def add_conditional_route(self, source_node_id, condition_port_id, condition_value, 
                             target_node_id, target_port_id=None, data_port_id=None):
        """
        Add a conditional route between nodes.
        
        Args:
            source_node_id (str): ID of the source node
            condition_port_id (str): ID of the port to evaluate for the condition
            condition_value: Value that condition_port must equal to take this route
            target_node_id (str): ID of the target node if condition is met
            target_port_id (str, optional): ID of the input port on the target node
            data_port_id (str, optional): ID of the output port to pass data from
                                         (defaults to condition_port_id)
        
        Returns:
            WorkflowBuilder: Self for method chaining
        """
        self.conditional_routes.append({
            "source_node_id": source_node_id,
            "condition_port_id": condition_port_id,
            "condition_value": condition_value,
            "target_node_id": target_node_id,
            "target_port_id": target_port_id or "input",
            "data_port_id": data_port_id or condition_port_id
        })
        return self
    
    def connect(self, source_node_id, source_port_id, target_node_id, target_port_id):
        """
        Create a connection between two nodes.
        
        Args:
            source_node_id (str): ID of the source node
            source_port_id (str): ID of the output port on the source node
            target_node_id (str): ID of the target node
            target_port_id (str): ID of the input port on the target node
            
        Returns:
            WorkflowBuilder: Self for method chaining
        """
        self.connections.append({
            "source_node_id": source_node_id,
            "source_port_id": source_port_id,
            "target_node_id": target_node_id,
            "target_port_id": target_port_id
        })
        return self
    
    def build(self):
        """
        Build and return the workflow.
        
        Returns:
            Workflow: The constructed workflow
        """
        import uuid
        
        # Generate ID if not provided
        workflow_id = self.workflow_id or str(uuid.uuid4())
        
        # Create the workflow
        workflow = Workflow(workflow_id, self.workflow_name, self.workflow_description)
        
        # Add nodes
        for node in self.nodes.values():
            workflow.add_node(node)
        
        # Add connections
        for connection in self.connections:
            workflow.connect(
                connection["source_node_id"],
                connection["source_port_id"],
                connection["target_node_id"],
                connection["target_port_id"]
            )

        for route in self.conditional_routes:
            workflow.add_conditional_route(
                route["source_node_id"],
                route["condition_port_id"],
                route["condition_value"],
                route["target_node_id"],
                route["target_port_id"],
                route.get("data_port_id")
            )

        # Validate workflow connections
        for node_id, node in workflow.nodes.items():
            for port_id, port_info in node.input_ports.items():
                # Skip validation for optional input ports
                if not port_info.get("required", True):
                    continue
                    
                # Check if any connection targets this port
                has_connection = any(
                    conn["target_node_id"] == node_id and conn["target_port_id"] == port_id
                    for conn in workflow.connections
                )
                
                # Check if any conditional route targets this port
                has_conditional = any(
                    route["target_node_id"] == node_id and route["target_port_id"] == port_id
                    for route in workflow.conditional_routes
                )
                
                # Determine if this is a start node (no incoming connections)
                is_start_node = not any(
                    conn["target_node_id"] == node_id
                    for conn in workflow.connections
                ) and not any(
                    route["target_node_id"] == node_id
                    for route in workflow.conditional_routes
                )
                
                # Start nodes can get inputs from context, so we don't validate their ports
                if not (has_connection or has_conditional) and not is_start_node:
                    raise ValueError(
                        f"Required input port '{port_id}' on node '{node_id}' ({node.name}) "
                        f"has no incoming connection"
                    )
        
        return workflow