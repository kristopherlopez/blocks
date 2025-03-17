"""
Base node implementation for workflow system.
"""

class BaseNode:
    """
    Base class for all workflow nodes.
    
    A node represents a single unit of work in a workflow with defined
    inputs and outputs.
    """
    
    def __init__(self, id, name, description=None):
        """
        Initialize a new node.
        
        Args:
            id (str): Unique identifier for the node
            name (str): Human-readable name
            description (str, optional): Detailed description
        """
        self.id = id
        self.name = name
        self.description = description
        self.input_ports = {}
        self.output_ports = {}
    
    def add_input_port(self, id, name, description=None, required=True):
        """
        Add an input port to the node.
        
        Args:
            id (str): Unique identifier for the port
            name (str): Human-readable name
            description (str, optional): Description of the port's purpose
            required (bool, optional): Whether this input is required
                
        Returns:
            BaseNode: Self for method chaining
        """
        self.input_ports[id] = {
            "name": name, 
            "description": description,
            "required": required
        }
        return self
    
    def add_output_port(self, id, name, description=None):
        """
        Add an output port to the node.
        
        Args:
            id (str): Unique identifier for the port
            name (str): Human-readable name
            description (str, optional): Description of the port's purpose
            
        Returns:
            BaseNode: Self for method chaining
        """
        self.output_ports[id] = {"name": name, "description": description}
        return self
    
    async def execute(self, inputs, context):
        """
        Execute the node's logic.
        
        Args:
            inputs (dict): Dictionary mapping input port IDs to values
            context (dict): Execution context information
            
        Returns:
            dict: Dictionary mapping output port IDs to values
            
        Raises:
            NotImplementedError: Subclasses must implement this method
        """
        raise NotImplementedError("Nodes must implement execute method")